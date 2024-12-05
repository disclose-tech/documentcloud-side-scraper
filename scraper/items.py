"""Models for the scraped items."""

from scrapy.item import Item, Field


class DocumentItem(Item):
    """A document that will be uploaded to DocumentCloud."""

    title = Field()
    project = Field()
    project_id = Field()
    year = Field()

    source = Field()
    access = Field()

    category = Field()
    category_local = Field()

    authority = Field()

    source_file_url = Field()
    source_filename = Field()
    source_page_url = Field()

    publication_date = Field()
    publication_time = Field()
    publication_datetime = Field()

    publication_timestamp = Field()
    publication_lastmodified = Field()

    info = Field()

    headers = Field()

    error = Field()

    # for zips
    file_from_zip = Field()
    local_file_path = Field()
    zip_seen_supported_files = Field()
    zip_seen_supported_number = Field()

    event_data_key = Field()
    source_file_zip_path = Field()

    departments = Field()
    departments_sources = Field()
