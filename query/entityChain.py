from langchain_core.pydantic_v1 import BaseModel, Field
from typing import List
from langchain_core.prompts import ChatPromptTemplate


def extract_question(llm):

    class Entities(BaseModel):
        """Identifying information about entities."""

        names: List[str] = Field(
            ...,
            description=
            "All the person, organization, business, or date entities that "
            "appear in the text",
        )

    prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            # "You are extracting organization and person entities from the text.",
            "You are extracting writing field entities from the text.",
        ),
        # (
        #     "system",
        #     "問題中有包含'原住民'或'原民'關鍵字，幫我擷取出以下關鍵字，原住民、阿美族、排灣族、泰雅族、布農族、太魯閣族、卑南族、賽夏族、達悟族",
        # ),
        (
            "human",
            "Use the given format to extract information from the following "
            "input: {question}",
        ),
    ])

    entity_chain = prompt | llm.with_structured_output(Entities)

    return entity_chain
