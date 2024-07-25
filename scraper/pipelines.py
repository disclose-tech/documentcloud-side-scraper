# Item Pipelines

import datetime
import re
import os
import shutil
from urllib.parse import urlparse
import logging
import json

import dateparser

from itemadapter import ItemAdapter

from scrapy.exceptions import DropItem
from documentcloud.constants import SUPPORTED_EXTENSIONS


class CountFilesInZipPipeline:

    def process_item(self, item, spider):

        if item["file_from_zip"]:
            item["zip_seen_supported_number"] = len(item["zip_seen_supported_files"])

        return item


class ParseDatePipeline:
    """Parse dates from scraped data."""

    def process_item(self, item, spider):
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
            # print(f'DEBUG: target_authority is "{item["target_authority"]}".')
            publication_dt = datetime.datetime.strptime(
                item["publication_lastmodified"], "%a, %d %b %Y %H:%M:%S GMT"
            )

        item["publication_timestamp"] = publication_dt.isoformat() + "Z"

        item["publication_date"] = publication_dt.strftime("%Y-%m-%d")
        item["publication_time"] = publication_dt.strftime("%H:%M:%S UTC")

        item["publication_datetime"] = (
            item["publication_date"] + " " + item["publication_time"]
        )

        return item


class CorrectYearPipeline:
    """Correct Year field based on project info."""

    """This is needed because the filter for the last year on SIDE includes documents from previous years where a decision hasn't been recorded."""

    def process_item(self, item, spider):

        # Extract all years from info
        years_in_info = re.findall("20\d\d", item["info"])

        years_in_info = [int(x) for x in years_in_info]

        if int(spider.target_year) in years_in_info:
            item["year"] = spider.target_year

        else:

            # in some cases, add the publication year
            if not "Date limite d'avis :" in item["info"]:

                publication_year = int(item["publication_date"][:4])

                years_in_info.append(publication_year)

            # Take the greatest year, set it as year

            max_year = max(years_in_info)

            item["year"] = max_year

        return item


class CategoryPipeline:
    """Attribute the final category of the document."""

    def process_item(self, item, spider):
        if "cas par cas" in item["category_local"].lower():
            item["category"] = "Cas par cas"

        elif item["category_local"] in ["Saisines pour avis", "Avis"]:
            item["category"] = "Avis"

        elif item["category_local"] in [
            "Saisines cadrage préalable",
            "Cadrages préalables",
        ]:
            item["category"] = "Cadrage"

        return item


class SourceFileNamePipeline:
    """Adds the source_file_name field based on source_file_url, or local_file_path for zip."""

    def process_item(self, item, spider):

        adapter = ItemAdapter(item)

        if not adapter.get("source_file_name"):

            path = urlparse(item["source_file_url"]).path

            item["source_file_name"] = os.path.basename(path)

        return item


class BeautifyPipeline:
    def process_item(self, item, spider):
        """Beautify & harmonize project & title names."""

        # Project

        item["project"] = item["project"].strip()
        item["project"] = item["project"].replace(" ", " ").replace("’", "'")
        item["project"] = item["project"].rstrip(".,")

        # if item["authority"] == "Ministère de l'Environnement":
        #     remove_at_start = [
        #         # Avis...
        #         "avis de l'autorité environnementale - ",
        #         "avis de l'autorité environnementale relatif au ",
        #         "avis d'autorité environnementale relatif au ",
        #         "avis de l'autorité environnementale relatif à l'",
        #         "avis de l'autorité environnementale relatif à la ",
        #         "avis de l'autorité environnementale sur le ",
        #         "avis de l'autorité environnementale :",
        #         "avis de l'autorité environnementale portant sur le ",
        #         "avis de l'autorité environnementale concernant le ",
        #         # Décision...
        #         "décision après examen au cas par cas relative au ",
        #         "décision d'examen au cas par cas relative au ",
        #         "décision après examen au cas par cas relative à la ",
        #         "décision après examen au cas par cas relative à l'",
        #         "décision après examen au cas par cas relative aux",
        #         "décision après examen aucas par cas relative au ",
        #         "décision après examen au cas par cas portant sur un ",
        #         "décision après examen au cas par cas sur le ",
        #         "décision après examen au cas par cas, sur le ",
        #         "décision cas par cas portant sur le ",
        #         "décision après examen au cas par cas, en application de l'article r.122.3 du code de l'environnement, sur le ",
        #         "décision après examen au cas par cas, en application de l'article r. 122.3 du code de l'environnement, pour le ",
        #         "décision de l'autorité environnementale après examen au cas par cas sur le ",
        #         "décision de l'autorité environnementale, après examen au cas par cas, sur le ",
        #         "décision de l'autorité environnementale portant sur le ",
        #         "décision de l'autorité environnementale, après examen au cas par cas, portant sur le ",
        #         "décision de l'autorité environnementale après examen au cas par cas concernant le ",
        #         # Demande...
        #         "demande d'examen au cas par cas relative au ",
        #         "demande d'examen au cas par relative au ",
        #         "demande d'examen au cas par cas du ",
        #         "demande d'examen au cas par cas relative à la ",
        #         "demande d'examen au cas par cas relative à l'",
        #         "demande d'examen au cas par cas pour la ",
        #         "demande au cas par cas pour le ",
        #         "demande d'examen au cas par cas :",
        #         "demande d'examen au cas par cas -",
        #         "demande d'examen au cas par cas: ",
        #         "demande d'examen au cas par cas concernant le ",
        #         "demande d'examen au cas par cas concernant un ",
        #         "demande d'examen au cas par cas portant sur la ",
        #         "demande d'examen au cas par cas relatif au ",
        #         # Retrait...
        #         "retrait de la demande d'examen au cas par cas : ",
        #     ]
        #     for start in remove_at_start:

        #         if item["project"].lower().startswith(start):
        #             item["project"] = item["project"][len(start) :]

        #     remove_at_start2 = ["dossier de"]

        #     for start in remove_at_start2:
        #         if item["project"].lower().startswith(start):
        #             item["project"] = item["project"][len(start) :]

        item["project"] = item["project"][0].capitalize() + item["project"][1:]

        # Title
        if item["file_from_zip"]:

            item["title"] = " - ".join(
                # [x.split(".")[0] for x in filepath.split("/")[2:]]
                [
                    x
                    for x in item["local_file_path"].split("/")[2:-1]
                    + [item["local_file_path"].split("/")[-1].split(".")[0]]
                ]
            )
        item["project"] = item["project"].replace("_", " ")
        item["title"] = item["title"].rstrip(".,")
        item["title"] = item["title"].strip()
        item["title"] = item["title"][0].capitalize() + item["title"][1:]

        return item


class UploadLimitPipeline:
    """Sends the signal to close the spider once the upload limit is attained."""

    def open_spider(self, spider):
        self.number_of_docs = 0

    def process_item(self, item, spider):
        self.number_of_docs += 1

        if spider.upload_limit == 0 or self.number_of_docs < spider.upload_limit + 1:
            return item
        else:
            spider.upload_limit_attained = True
            raise DropItem("Upload limit exceeded.")


class UploadPipeline:
    """Upload document to DocumentCloud & store event data."""

    def open_spider(self, spider):

        documentcloud_logger = logging.getLogger("documentcloud")
        documentcloud_logger.setLevel(logging.WARNING)

        if not spider.dry_run:
            try:
                spider.event_data = spider.load_event_data()

            except Exception as e:
                raise Exception("Error loading event data").with_traceback(
                    e.__traceback__
                )
                sys.exit(1)
        else:
            spider.event_data = None

        if spider.event_data is None:
            spider.event_data = {"documents": {}, "zips": {}}

        if spider.dry_run:
            spider.logger.info(f"Event data not loaded (dry run)")
        else:
            spider.logger.info(
                f"Loaded event data ({len(spider.event_data['documents'])} documents, {len(spider.event_data['zips'])} zip files)"
            )

    def process_item(self, item, spider):

        filename, file_extension = os.path.splitext(item["source_file_name"])
        file_extension = file_extension.lower()

        # File path and event_data_key
        if item["file_from_zip"]:
            file_path = item["local_file_path"]
            print("DEBUG: ZIP PROCESSED!")

            item["source_file_zip_path"] = os.path.join(
                *item["local_file_path"].split(os.sep)[2:]
            )

            item["event_data_key"] = (
                item["source_file_url"] + "/" + item["source_file_zip_path"]
            )
        else:
            file_path = item["source_file_url"]
            item["event_data_key"] = item["source_file_url"]

        if not spider.dry_run:

            if file_extension not in SUPPORTED_EXTENSIONS:
                spider.logger.warning(
                    f"Unsupported filetype, not uploading {item['source_file_name']} (url: {item['source_file_url']}, page: {item['source_page_url']}) "
                )
            else:  # supported file extension
                data = {
                    "authority": item["authority"],
                    "category": item["category"],
                    "category_local": item["category_local"],
                    "event_data_key": item["event_data_key"],
                    "source_scraper": "SIDE Scraper",
                    "source_file_url": item["source_file_url"],
                    "source_file_name": item["source_file_name"],
                    "source_page_url": item["source_page_url"],
                    "publication_date": item["publication_date"],
                    "publication_time": item["publication_time"],
                    "publication_datetime": item["publication_datetime"],
                    "year": str(item["year"]),
                }

                if item["file_from_zip"]:
                    data["source_file_zip_path"] = item["source_file_zip_path"]

                try:
                    spider.client.documents.upload(
                        file_path,
                        original_extension=file_extension.lstrip("."),
                        project=spider.target_project,
                        title=item["title"],
                        description=item["project"],
                        source="side.developpement-durable.gouv.fr",
                        language="fra",
                        access=spider.access_level,
                        data=data,
                    )
                except Exception as e:
                    raise Exception("Upload error").with_traceback(e.__traceback__)

                else:  # No upload error, add to event_data

                    now = datetime.datetime.now().isoformat()

                    # Zip files
                    if item["file_from_zip"]:

                        # Add the file to event_data documents

                        item_relative_filepath = os.path.join(
                            *item["local_file_path"].split(os.sep)[2:]
                        )

                        event_data_path = (
                            item["source_file_url"] + "/" + item_relative_filepath
                        )

                        spider.event_data["documents"][item["event_data_key"]] = {
                            "last_modified": item["publication_lastmodified"],
                            "last_seen": now,
                        }

                        # Check whether all files of the zip are in event_data documents
                        zip_fully_processed = True

                        for seen_file_path in item["zip_seen_supported_files"]:
                            file_event_data_path = (
                                item["source_file_url"] + "/" + seen_file_path
                            )

                            if (
                                file_event_data_path
                                not in spider.event_data["documents"]
                            ):
                                zip_fully_processed = False

                        if zip_fully_processed:
                            spider.event_data["zips"][item["source_file_url"]] = {
                                "last_modified": item["publication_lastmodified"],
                                "last_seen": now,
                            }

                    else:  # Not a file from a zip

                        spider.event_data["documents"][item["event_data_key"]] = {
                            "last_modified": item["publication_lastmodified"],
                            "last_seen": now,
                        }

                    # Store event_data (# only from the web interface)
                    if spider.run_id:
                        spider.store_event_data(spider.event_data)

        return item

    def close_spider(self, spider):
        """Update event data when the spider closes."""

        if not spider.dry_run and spider.run_id:
            spider.store_event_data(spider.event_data)
            spider.logger.info(
                f"Uploaded event data ({len(spider.event_data['documents'])} documents, {len(spider.event_data['zips'])} zip files)"
            )

        # if not spider.run_id:
        #     with open("event_data.json", "w") as file:
        #         json.dump(spider.event_data, file)
        #         spider.logger.info(
        #             f"Saved file event_data.json ({len(spider.event_data['documents'])} documents, {len(spider.event_data['zips'])} zip files)"
        #         )


class MailPipeline:
    """Send scraping run report when the spider closes."""

    def open_spider(self, spider):
        self.scraped_items = []

    def process_item(self, item, spider):

        self.scraped_items.append(item)

        return item

    def close_spider(self, spider):

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
            """

            return item_string

        subject = (
            f"SIDE Scraper {str(spider.target_year)} (New: {len(self.scraped_items)} )"
        )

        # errors_content = f"ERRORS ({len(self.items_with_error)})\n\n" + "\n\n".join(
        #     [print_item(item, error=True) for item in self.items_with_error]
        # )

        ok_content = f"SCRAPED ITEMS ({len(self.scraped_items)})\n\n" + "\n\n".join(
            [print_item(item) for item in self.scraped_items]
        )

        start_content = f"SIDE Scraper Addon Run {spider.run_id}"

        content = "\n\n".join([start_content, ok_content])

        if not spider.dry_run:
            spider.send_mail(subject, content)


class DeleteZipFilesPipeline:
    """Delete files from downloaded zips to save some disk space"""

    def process_item(self, item, spider):
        if item["file_from_zip"]:
            if os.path.isfile(item["local_file_path"]):
                # print(f"Deleting {item['local_file_path']}...")
                os.remove(item["local_file_path"])

        return item

    def close_spider(self, spider):

        # Delete the downloaded_zips folder
        if os.path.isdir("downloaded_zips"):
            shutil.rmtree("downloaded_zips")