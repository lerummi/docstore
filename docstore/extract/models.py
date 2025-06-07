from pydantic import Field, BaseModel
from typing import List, Dict, Any


class EcoiHtmlProperties(BaseModel):
    """
    Basic attributes associcated with a single www.ecoi.com html page refering to a report document.
    """
    country: str = Field(
        description=
            "Country the document is about. "
            "The demanded value $country can be found by looking for <dt>Country:</dt><dd>$country</dd>. "
            "Transform the value $country into a list of countries in case multiple countries are named. No text arround the countries."
        #examples=["Afghanistan", "Iran", "China"]
    )
    published: str = Field(
        description=
            "Publication date of the document. "
            "The demanded value $published can be found by looking for <dt>Published:</dt><dd>$published<dd>. "
            "Transform value $published such that its format is **strictly** %Y-%m-%d.",
        #examples=["2024-03-05", "1998-11-19", "2005-07-30"]
    )
    document_type: str = Field(
        description=
            "Type of the document. "
            "The value $document_type can be found by looking for <dt>Document type:</dt><dd>$document_type<dd>.",
        #examples=["Media Report", "Appeal or News Release", "Expert Opinion or Position"]
    )
    language: str = Field(
        description=
            "Language the document is published in. " 
            "The value $language can be found by looking for <dt>Language:</dt><dd>$language<dd>. "
            "Transform value $language to be the **full** name of an existing language in case it is an abbreviation, i.e. en -> English, fr -> French etc.",
        #examples=["English", "French", "German"]
    )
    document_id: int = Field(
        description=
            "Id of the document. "
            "The value $document_id can be found by looking for <dt>Document ID:</dt><dd>$document_id<dd>. "
            "The value $document_id **must** be an integer and usually has 7 digits.",
        #examples=[2125368, 1013972, 1832837]
    )
    original_link: str = Field(
        description=
            "Original link associated with the document. "
            """The value $original_link Whitespaces can be found by looking for <dt>Original link:</dt><dd class="link"><a target="_blank" rel="noopener" href="$original_link">$original_link</a><dd>'.""",
        #examples=[
        #    "https://www.ecoi.net/en/file/local/1000295/1002_1264804179_jordan.PDF",
        #    "https://www.amnesty.de/informieren/amnesty-journal/syrien-befehlskette-gegen-die-menschlichkeit",
        #    "http://www.lib.utexas.edu/maps/africa/mauritania_pol95.jpg"
        #]    
    )


class OpenAIRequest(BaseModel):
    model: str = Field(default="pt-4.1-nano")
    instructions: str = Field(
        default=
            "You are a expert information extractor. "
            "You are expert in reading html format and extract information required to be retrieved. "
            "In the given html, you find the values exactly as described and apply transformations if requested to full satisfaction."
    )
    input: List[Dict[str, Any]]
    text: Dict[str, Any]

