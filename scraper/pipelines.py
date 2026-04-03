# Item Pipelines

import datetime
import re
import os
import shutil
import sys
from urllib.parse import urlparse
import logging
import json
import hashlib

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from documentcloud.constants import SUPPORTED_EXTENSIONS

from .log import SilentDropItem

from .departments import department_from_authority, departments_from_project_name


class SpiderPipeline:
    """Base class for pipelines that need access to the spider instance.

    Provides from_crawler() to store spider as self.spider.
    Inherit from this class instead of defining from_crawler() in each pipeline.
    """

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        pipeline.spider = crawler.spider
        return pipeline


class ParseDatePipeline:
    """Parse dates from scraped data."""

    def process_item(self, item):
        """Parse date from the extracted string."""

        # Publication date
        if item["authority"] in [
            "Ministère de l'Environnement",
            "Préfecture de région La Réunion",
        ]:
            publication_dt = datetime.datetime.strptime(
                item["publication_lastmodified"], "%Y%m%d%H%M%S"
            )
        else:
            publication_dt = datetime.datetime.strptime(
                item["publication_lastmodified"], "%a, %d %b %Y %H:%M:%S GMT"
            )

        item["publication_timestamp"] = publication_dt.isoformat() + "Z"

        item["publication_date"] = publication_dt.strftime("%Y-%m-%d")
        item["publication_time"] = publication_dt.strftime("%H:%M:%S UTC")

        item["publication_datetime"] = (
            item["publication_date"] + " " + item["publication_time"]
        )

        item["publication_datetime_dcformat"] = (
            publication_dt.isoformat(timespec="microseconds") + "Z"
        )

        return item


class CategoryPipeline:
    """Attribute the final category of the document."""

    def process_item(self, item):
        if "cas par cas" in item["category_local"].lower():
            item["category"] = "Cas par cas"

        elif item["category_local"] in [
            "Saisines pour avis",
            "Avis",
            "Avis sur les Projets",
        ]:
            item["category"] = "Avis"

        elif item["category_local"] in [
            "Saisines cadrage préalable",
            "Cadrages préalables",
        ]:
            item["category"] = "Cadrage"

        return item


class SourceFileNamePipeline:
    """Adds the source_filename field based on source_file_url, or local_file_path for zip."""

    def process_item(self, item):

        adapter = ItemAdapter(item)

        if not adapter.get("source_filename"):

            path = urlparse(item["source_file_url"]).path

            item["source_filename"] = os.path.basename(path)

        return item


class BeautifyPipeline:
    def process_item(self, item):
        """Beautify & harmonize metadata."""

        # Project

        item["project"] = item["project"].strip()
        item["project"] = item["project"].replace(" ", " ").replace("’", "'")
        item["project"] = item["project"].rstrip(".,")
        item["project"] = item["project"][0].capitalize() + item["project"][1:]

        # Projet_01 > Project (01)
        item["project"] = re.sub(
            r"_([02][1-9]|2[AB]|[1345678][0-9]|9[012345]|97[1-8])$",
            r" (\1)",
            item["project"],
        )
        # Add missing parenthesis at the end
        item["project"] = re.sub(
            r"\(([02][1-9]|2[AB]|[1345678][0-9]|9[012345]|97[1-8])$",
            r"(\1)",
            item["project"],
        )

        # Title
        if item["file_from_zip"]:

            item["title"] = " - ".join(
                # folder1/folder2/document.pdf => folder1 - folder2 - document
                [
                    x
                    # folders
                    for x in item["local_file_path"].split("/")[2:-1]
                    # filename without extension
                    + [os.path.splitext(os.path.basename(item["local_file_path"]))[0]]
                ]
            )

        item["title"] = item["title"].replace("_", " ")
        item["title"] = item["title"].rstrip(".,")
        item["title"] = item["title"].strip()
        item["title"] = item["title"][0].capitalize() + item["title"][1:]

        # Authority

        if item["authority"] == "Préfecture de région Île de France":
            item["authority"] = "Préfecture de région Île-de-France"

        if item["authority"] == "Préfecture de région Bourgogne-Franche Comté":
            item["authority"] = "Préfecture de région Bourgogne-Franche-Comté"

        if item["authority"] == "Préfecture de région Hauts de France":
            item["authority"] = "Préfecture de région Hauts-de-France"

        if item["authority"] == "Préfecture de région Nouvelle Aquitaine":
            item["authority"] = "Préfecture de région Nouvelle-Aquitaine"

        return item


class UnsupportedFiletypePipeline:

    def process_item(self, item):

        filename, file_extension = os.path.splitext(item["source_filename"])
        file_extension = file_extension.lower()

        if file_extension not in SUPPORTED_EXTENSIONS:

            # If the file comes from a zip, remove it
            if item["file_from_zip"]:
                if os.path.isfile(item["local_file_path"]):
                    # print(f"Deleting {item['local_file_path']}...")
                    os.remove(item["local_file_path"])
            # Drop the item
            raise DropItem("Unsupported filetype")
        else:
            return item


class UploadLimitPipeline(SpiderPipeline):
    """Sends the signal to close the spider once the upload limit is attained."""

    def open_spider(self):
        self.number_of_docs = 0

    def process_item(self, item):
        self.number_of_docs += 1

        if (
            self.spider.upload_limit == 0
            or self.number_of_docs < self.spider.upload_limit + 1
        ):
            return item
        else:
            self.spider.upload_limit_attained = True
            raise SilentDropItem("Upload limit exceeded.")


class TagDepartmentsPipeline:

    def process_item(self, item):

        authority_department = department_from_authority(item["authority"])

        if authority_department:
            item["departments_sources"] = ["authority"]
            item["departments"] = [authority_department]

        else:

            project_departments = departments_from_project_name(item["project"])

            if project_departments:

                item["departments_sources"] = ["regex"]
                item["departments"] = project_departments

        return item


class ProjectIDPipeline:

    def process_item(self, item):

        project_name = item["project"]
        source_page_url = item["source_page_url"]
        string_to_hash = source_page_url + " " + project_name

        hash_object = hashlib.sha256(string_to_hash.encode())
        hex_dig = hash_object.hexdigest()

        item["project_id"] = hex_dig

        return item


class UploadPipeline(SpiderPipeline):
    """Upload document to DocumentCloud & store event data."""

    def open_spider(self):

        documentcloud_logger = logging.getLogger("documentcloud")
        documentcloud_logger.setLevel(logging.WARNING)

        if not self.spider.dry_run:
            try:
                self.spider.logger.info("Loading event data from DocumentCloud...")
                self.spider.event_data = self.spider.load_event_data()

            except Exception as e:
                raise Exception("Error loading event data").with_traceback(
                    e.__traceback__
                )
                sys.exit(1)
        else:
            # Load from json if present
            try:
                self.spider.logger.info("Loading event data from local JSON file...")
                with open("event_data.json", "r") as file:
                    data = json.load(file)

                    self.spider.event_data = {
                        "documents": data["documents"],
                        "zips": data["zips"],
                    }
            except:
                self.spider.event_data = None

        if self.spider.event_data:
            self.spider.logger.info(
                f"Loaded event data ({len(self.spider.event_data['documents'])} documents, {len(self.spider.event_data['zips'])} zip files)"
            )
        else:
            self.spider.event_data = {"documents": {}, "zips": {}}

        self.spider.logger.info(
            f"Loaded event data ({len(self.spider.event_data['documents'])} documents, {len(self.spider.event_data['zips'])} zip files)"
        )

    def process_item(self, item):

        filename, file_extension = os.path.splitext(item["source_filename"])
        file_extension = file_extension.lower()

        # File path and event_data_key
        if item["file_from_zip"]:
            file_path = item["local_file_path"]

            item["source_file_zip_path"] = os.path.join(
                *item["local_file_path"].split(os.sep)[2:]
            )

            item["event_data_key"] = (
                item["source_file_url"] + "/" + item["source_file_zip_path"]
            )
        else:
            file_path = item["source_file_url"]
            item["event_data_key"] = item["source_file_url"]

        data = {
            "authority": item["authority"],
            "category": item["category"],
            "category_local": item["category_local"],
            "event_data_key": item["event_data_key"],
            "source_scraper": "SIDE Scraper",
            "source_scraper_year": str(item["year"]),
            "source_file_url": item["source_file_url"],
            "source_filename": item["source_filename"],
            "source_page_url": item["source_page_url"],
            "publication_date": item["publication_date"],
            "publication_time": item["publication_time"],
            "publication_datetime": item["publication_datetime"],
            "project_id": item["project_id"],
        }
        if item["file_from_zip"]:
            data["source_file_zip_path"] = item["source_file_zip_path"]

        adapter = ItemAdapter(item)
        if adapter.get("departments") and adapter.get("departments_sources"):
            data["departments"] = item["departments"]
            data["departments_sources"] = item["departments_sources"]

        try:
            if not self.spider.dry_run:
                self.spider.client.documents.upload(
                    file_path,
                    original_extension=file_extension.lstrip("."),
                    project=self.spider.target_project,
                    title=item["title"],
                    description=item["project"],
                    publish_at=item["publication_datetime_dcformat"],
                    source="side.developpement-durable.gouv.fr",
                    language="fra",
                    access=self.spider.access_level,
                    data=data,
                )

        except Exception as e:
            raise Exception("Upload error").with_traceback(e.__traceback__)

        else:  # No upload error, add to event_data
            last_modified = item["publication_timestamp"][:-1]  # remove Z at the end.
            now = datetime.datetime.now().isoformat(timespec="seconds")

            self.spider.event_data["documents"][item["event_data_key"]] = {
                "last_modified": last_modified,
                "last_seen": now,
                "target_year": item["year"],
            }
            # Zip files
            if item["file_from_zip"]:
                # Check whether all files of the zip are in event_data documents
                zip_fully_processed = True
                for seen_file_path in item["zip_seen_supported_files"]:
                    file_event_data_path = (
                        item["source_file_url"] + "/" + seen_file_path
                    )
                    if file_event_data_path not in self.spider.event_data["documents"]:
                        zip_fully_processed = False
                if zip_fully_processed:
                    self.spider.event_data["zips"][item["source_file_url"]] = {
                        "last_modified": last_modified,
                        "last_seen": now,
                        "target_year": item["year"],
                    }

            # Store event_data (# only from the web interface)
            if self.spider.run_id and not self.spider.dry_run:
                self.spider.store_event_data(self.spider.event_data)

        return item

    def close_spider(self):
        """Update event data when the spider closes."""

        if not self.spider.dry_run and self.spider.run_id:
            if self.spider.event_data:
                self.spider.store_event_data(self.spider.event_data)
                self.spider.logger.info(
                    f"Uploaded event data ({len(self.spider.event_data['documents'])} documents, {len(self.spider.event_data['zips'])} zip files)"
                )

                # Upload the event_data to the DocumentCloud interface
                now = datetime.datetime.now()
                timestamp = now.strftime("%Y%m%d_%H%M")
                filename = f"event_data_SIDE_{timestamp}.json"

                if self.spider.upload_event_data:
                    with open(filename, "w+") as event_data_file:
                        json.dump(self.spider.event_data, event_data_file)
                        self.spider.upload_file(event_data_file)
                    self.spider.logger.info(
                        f"Uploaded event data to the Documentcloud interface."
                    )

            else:
                self.spider.logger.info("No event data to upload.")

        if not self.spider.run_id:
            if self.spider.event_data:
                with open("event_data.json", "w") as file:
                    json.dump(self.spider.event_data, file)
                    self.spider.logger.info(
                        f"Saved file event_data.json ({len(self.spider.event_data['documents'])} documents, {len(self.spider.event_data['zips'])} zip files)"
                    )
            else:
                self.spider.logger.info("No event data to write.")


class MailPipeline(SpiderPipeline):
    """Send scraping run report when the spider closes."""

    def open_spider(self):
        self.scraped_items = []

    def process_item(self, item):

        self.scraped_items.append(item)

        return item

    def close_spider(self):

        def print_item(item):
            item_string = f"""
            title: {item["title"]}
            project: {item["project"]}
            authority: {item["authority"]}
            category: {item["category"]}
            category_local: {item["category_local"]}
            year: {item["year"]}
            publication_date: {item["publication_date"]}
            source_filename: {item["source_filename"]}
            source_file_url: {item["source_file_url"]}
            source_page_url: {item["source_page_url"]}
            event_data_key: {item["event_data_key"]}
            """

            return item_string

        if len(self.spider.target_years) == 1:
            year_range_str = str(self.spider.target_years[0])
        else:
            year_range_str = f"{str(self.spider.target_years[0])}-{str(self.spider.target_years[-1])}"

        subject = f"SIDE Scraper {year_range_str} (New: {len(self.scraped_items)}) [{self.spider.run_name}]"

        # errors_content = f"ERRORS ({len(self.items_with_error)})\n\n" + "\n\n".join(
        #     [print_item(item, error=True) for item in self.items_with_error]
        # )

        ok_content = f"SCRAPED ITEMS ({len(self.scraped_items)})\n\n" + "\n\n".join(
            [print_item(item) for item in self.scraped_items]
        )

        start_content = f"SIDE Scraper Addon Run {self.spider.run_id}"

        content = "\n\n".join([start_content, ok_content])

        if not self.spider.dry_run:
            self.spider.send_mail(subject, content)


class DeleteZipFilesPipeline:
    """Delete files from downloaded zips to save some disk space"""

    def process_item(self, item):

        if item["file_from_zip"]:
            if os.path.isfile(item["local_file_path"]):
                # print(f"Deleting {item['local_file_path']}...")
                os.remove(item["local_file_path"])

        return item

    def close_spider(self):

        # Delete the downloaded_zips folder
        if os.path.isdir("downloaded_files"):
            shutil.rmtree("downloaded_files")
