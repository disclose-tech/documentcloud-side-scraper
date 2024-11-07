# import datetime
import re
import json
import os
from urllib.parse import urlsplit
from zipfile import ZipFile
from pathlib import Path
from datetime import datetime, timedelta

import scrapy
from scrapy.http import Request
from scrapy.exceptions import CloseSpider

from documentcloud.constants import SUPPORTED_EXTENSIONS

from ..items import DocumentItem
from .utils import (
    SEARCH_ENDPOINT,
    LIST_DOCUMENTS_ENDPOINT,
    DOWNLOAD_ENDPOINT,
    AE_CGDD,
    REGIONS,
    REGIONS_SPECIAL_CASES,
    HEADERS,
    HEADERS2,
    make_json_data,
    make_region_config,
)


class SideSpider(scrapy.Spider):
    name = "SIDE_spider"

    # allowed_domains = [
    #     "side.developpement-durable.gouv.fr",
    #     "autorite-environnementale-entrepot.developpement-durable.gouv.fr",
    # ]

    upload_limit_attained = False

    start_time = datetime.now()

    def check_time_limit(self):
        """Closes the spider automatically if it reaches the time limit"""

        if self.time_limit != 0:

            limit = self.time_limit * 60
            now = datetime.now()

            if timedelta.total_seconds(now - self.start_time) > limit:
                raise CloseSpider(
                    f"Closed due to time limit ({self.time_limit} minutes)"
                )

    def check_upload_limit(self):
        """Closes the spider if the upload limit is attained."""
        if self.upload_limit_attained:
            raise CloseSpider("Closed due to max documents limit.")

    def start_requests(self):

        # Toggles
        ae_ministre = True
        ae_region = True
        ae_region_specialcases = True

        # AE Ministre
        if ae_ministre:
            for category in AE_CGDD["categories"]:

                catalogue = AE_CGDD["catalogue"]
                json_data = make_json_data(
                    query_string=AE_CGDD["categories"][category],
                    scenario_code=AE_CGDD["scenario_code"],
                    year_filter=AE_CGDD["year_filter"],
                    target_year=self.target_year,
                )

                yield Request(
                    url=SEARCH_ENDPOINT.format(catalogue=catalogue),
                    headers=HEADERS,
                    method="POST",
                    body=json.dumps(json_data),
                    callback=self.parse_projects_list,
                    cb_kwargs=dict(
                        authority="Ministère de l'Environnement",
                        catalogue=catalogue,
                        category=category,
                        page=0,
                        year_filter=AE_CGDD["year_filter"],
                    ),
                )

        # AE Préfet de région
        if ae_region:
            for region in REGIONS:

                catalogue = "PAE"
                config = make_region_config(region)

                for category in config["categories"]:

                    json_data = make_json_data(
                        query_string=config["categories"][category],
                        scenario_code="AE-GENERAL",
                        year_filter=config["year_filter"],
                        target_year=self.target_year,
                    )

                    yield Request(
                        url=SEARCH_ENDPOINT.format(catalogue=catalogue),
                        headers=HEADERS,
                        method="POST",
                        body=json.dumps(json_data),
                        callback=self.parse_projects_list,
                        cb_kwargs=dict(
                            authority=f"Préfecture de région {region}",
                            catalogue=catalogue,
                            category=category,
                            page=0,
                            year_filter=config["year_filter"],
                        ),
                    )

        # Special cases
        if ae_region_specialcases:
            for region in REGIONS_SPECIAL_CASES:

                catalogue = REGIONS_SPECIAL_CASES[region]["catalogue"]

                for category in REGIONS_SPECIAL_CASES[region]["categories"]:

                    json_data = json_data = make_json_data(
                        query_string=REGIONS_SPECIAL_CASES[region]["categories"][
                            category
                        ],
                        scenario_code=REGIONS_SPECIAL_CASES[region]["scenario_code"],
                        year_filter=REGIONS_SPECIAL_CASES[region]["year_filter"],
                        target_year=self.target_year,
                    )

                    yield Request(
                        url=SEARCH_ENDPOINT.format(catalogue=catalogue),
                        headers=HEADERS,
                        method="POST",
                        body=json.dumps(json_data),
                        callback=self.parse_projects_list,
                        cb_kwargs=dict(
                            authority=f"Préfecture de région {region}",
                            catalogue=catalogue,
                            category=category,
                            page=0,
                            year_filter=REGIONS_SPECIAL_CASES[region]["year_filter"],
                        ),
                    )

    def parse_projects_list(
        self,
        response,
        year_filter,
        authority,
        catalogue,
        category,
        page,
    ):

        self.check_upload_limit()
        self.check_time_limit()

        response_dict = json.loads(response.text)

        if response_dict == None:
            self.logger.error(
                f"Error parsing projects list, none returned: {authority}, {category}, {page})"
            )

        current_page = page
        max_page = response_dict["d"]["SearchInfo"]["PageMax"]

        if not max_page == -1:
            self.logger.info(
                f"{authority} - {category} ({self.target_year}): Scraping page {current_page+1}/{max_page+1}"
            )
        else:
            self.logger.info(
                f"{authority} - {category} ({self.target_year}): No results"
            )

        results = response_dict["d"]["Results"]

        if results:
            for r in results:

                # Check if the project has viewable docs
                has_primary_docs = r["HasPrimaryDocs"]
                has_digital_ready_docs = r["HasDigitalReady"]

                if has_primary_docs:

                    yield Request(
                        url=r["FriendlyUrl"],
                        callback=self.parse_project_page,
                        cb_kwargs=dict(
                            authority=authority,
                            catalogue=catalogue,
                            category=category,
                            project=r["Resource"]["Ttl"],
                            rsc_id=r["Resource"]["RscId"],
                            has_digital_ready_docs=has_digital_ready_docs,
                            year_filter=year_filter,
                        ),
                    )

        # Parse next page
        if current_page < max_page:

            json_data = make_json_data(
                query_string=response_dict["d"]["Query"]["QueryString"],
                scenario_code=response_dict["d"]["Query"]["ScenarioCode"],
                page=page + 1,
                target_year=self.target_year,
                year_filter=year_filter,
            )
            yield Request(
                url=SEARCH_ENDPOINT.format(catalogue=catalogue),
                headers=HEADERS,
                method="POST",
                body=json.dumps(json_data),
                callback=self.parse_projects_list,
                cb_kwargs=dict(
                    authority=authority,
                    catalogue=catalogue,
                    category=category,
                    page=page + 1,
                    year_filter=year_filter,
                ),
            )

    def parse_project_page(
        self,
        response,
        authority,
        catalogue,
        category,
        project,
        rsc_id,
        has_digital_ready_docs,
        year_filter,
    ):

        self.check_upload_limit()
        self.check_time_limit()

        if catalogue == "REUN":
            info = response.css(".item-datepublication").css("::text").get().strip()

        else:
            info = "\n".join(
                x.strip() for x in response.css("#tab2 ::text").getall() if x.strip()
            )

        if has_digital_ready_docs:
            yield Request(
                url=LIST_DOCUMENTS_ENDPOINT.format(
                    catalogue=catalogue.lower(), parent_document_id=rsc_id, start=0
                ),
                headers=HEADERS2,
                callback=self.parse_documents_list,
                cb_kwargs=dict(
                    authority=authority,
                    category=category,
                    catalogue=catalogue,
                    project=project,
                    rsc_id=rsc_id,
                    source_page_url=response.request.url,
                    info=info,
                    start=0,
                ),
            )
        else:
            # extract documents appearing on the side
            primary_docs_links = response.css("#document_actions .primarydoc")

            for link in primary_docs_links:
                link_text = link.css("span:last-of-type ::text").get()
                link_href = link.attrib["href"]
                link_href = link_href.replace("http://", "https://")
                link_text = link_text.replace("Consulter le ", "")
                link_text = link_text.replace("Consulter la ", "")

                if (
                    link_href not in self.event_data["documents"]
                    and link_href not in self.event_data["zips"]
                ):
                    doc_item = DocumentItem(
                        title=link_text,
                        project=project,
                        category_local=category,
                        authority=authority,
                        source_file_url=link_href,
                        source_page_url=response.request.url,
                        info=info,
                    )

                    yield Request(
                        url=link_href,
                        method="HEAD",
                        headers=HEADERS,
                        callback=self.parse_document_headers,
                        cb_kwargs=dict(doc_item=doc_item),
                    )

    def parse_documents_list(
        self,
        response,
        authority,
        catalogue,
        category,
        project,
        rsc_id,
        source_page_url,
        info,
        start,
    ):
        self.check_upload_limit()
        self.check_time_limit()

        response_dict = json.loads(response.body)

        results = response_dict["d"]["documents"]

        if results:

            for doc in results:
                source_file_url = DOWNLOAD_ENDPOINT.format(
                    catalogue=catalogue.lower(),
                    parent_document_id=rsc_id,
                    document_id=doc["documentId"],
                )

                if not source_file_url in self.event_data["documents"]:
                    yield DocumentItem(
                        title=doc["title"],
                        project=project,
                        category_local=category,
                        authority=authority,
                        source_file_url=source_file_url,
                        source_filename=doc["fileName"],
                        source_page_url=source_page_url,
                        publication_lastmodified=doc["whenUpdated"],
                        info=info,
                        file_from_zip=False,
                    )

            # Next pages
            if (
                response_dict["d"]["start"] + len(results)
                < response_dict["d"]["totalCount"]
            ):
                start += 10
                yield Request(
                    url=LIST_DOCUMENTS_ENDPOINT.format(
                        catalogue=catalogue.lower(), parent_document_id=rsc_id, start=0
                    ),
                    headers=HEADERS2,
                    callback=self.parse_documents_list,
                    cb_kwargs=dict(
                        authority=authority,
                        catalogue=catalogue,
                        category=category,
                        project=project,
                        rsc_id=rsc_id,
                        source_page_url=response.request.url,
                    ),
                )

    def parse_document_headers(self, response, doc_item):

        self.check_upload_limit()
        self.check_time_limit()

        doc_item["publication_lastmodified"] = response.headers.get(
            "Last-Modified"
        ).decode("utf-8")

        # Detect zip files and process them separately
        if doc_item["source_file_url"].lower().endswith(".zip"):

            yield Request(
                url=response.request.url,
                headers=HEADERS,
                callback=self.parse_zip_file,
                cb_kwargs=dict(doc_item=doc_item),
            )

        else:
            doc_item["file_from_zip"] = False
            yield doc_item

    def parse_zip_file(self, response, doc_item):

        # Get the modification date of the zip in the headers
        publication_lastmodified = response.headers.get("Last-Modified").decode("utf-8")

        # Get the filename from the requested URL
        urlpath = urlsplit(response.request.url).path
        filename = os.path.basename(urlpath)

        # Create the folder to hold zip files if it does not exist yet
        if not os.path.exists("./downloaded_zips"):
            os.makedirs("./downloaded_zips")

        # Save the zip file in the folder
        with open(f"./downloaded_zips/{filename}", "wb") as file:
            file.write(response.body)

        # Create a folder to hold the extracted files
        extracted_files_folder = f"./downloaded_zips/{filename[:-4]}"
        if not os.path.exists(extracted_files_folder):
            os.makedirs(extracted_files_folder)

        # Open Zip file and extract files
        with ZipFile(f"./downloaded_zips/{filename}", "r") as zip_file:
            zip_file.extractall(path=extracted_files_folder)

        # Delete zip file
        os.remove(f"./downloaded_zips/{filename}")

        # List files
        extracted_files_folder_path_obj = Path(extracted_files_folder)
        extracted_files_list = list(extracted_files_folder_path_obj.rglob("*"))

        # Make a list of seen files for event_data
        zip_seen_supported_files = []

        for f in extracted_files_list:
            if f.is_file():
                basename = os.path.basename(str(f))

                filename, file_ext = os.path.splitext(basename)

                if file_ext.lower() in SUPPORTED_EXTENSIONS:

                    relative_filepath = "/".join(str(f).split("/")[2:])

                    zip_seen_supported_files.append(relative_filepath)

        # Yield an object for each one
        for f in extracted_files_list:
            if f.is_file():
                filepath = str(f)

                item_relative_filepath = os.path.join(*filepath.split(os.sep)[2:])

                event_data_path = (
                    doc_item["source_file_url"] + "/" + item_relative_filepath
                )

                if not event_data_path in self.event_data["documents"]:
                    yield DocumentItem(
                        project=doc_item["project"],
                        category_local=doc_item["category_local"],
                        authority=doc_item["authority"],
                        source_file_url=response.request.url,
                        source_filename=f.name,
                        source_page_url=doc_item["source_page_url"],
                        publication_lastmodified=publication_lastmodified,
                        info=doc_item["info"],
                        local_file_path=str(f),
                        zip_seen_supported_files=zip_seen_supported_files,
                        file_from_zip=True,
                    )
