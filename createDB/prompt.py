from langchain_core.prompts import ChatPromptTemplate


def getPrompt():
    system_prompt = (
        "# Knowledge Graph Instructions for GPT-4\n"
        "## 1. Overview\n"
        "You are a top-tier algorithm designed for extracting information in structured "
        "formats to build a knowledge graph.\n"
        "Try to capture as much information from the text as possible without "
        "sacrifing accuracy. Do not add any information that is not explicitly "
        "mentioned in the text\n"
        "- **Nodes** represent entities and concepts.\n"
        "- The aim is to achieve simplicity and clarity in the knowledge graph, making it\n"
        "accessible for a vast audience.\n"
        "## 2. Labeling Nodes\n"
        "- **Consistency**: Ensure you use available types for node labels.\n"
        "Ensure you use basic or elementary types for node labels.\n"
        "- For example, when you identify an entity representing a person, "
        "always label it as **'person'**. Avoid using more specific terms "
        "like 'mathematician' or 'scientist'"
        "  - **Node IDs**: Never utilize integers as node IDs. Node IDs should be "
        "names or human-readable identifiers found in the text.\n"
        "- **Relationships** represent connections between entities or concepts.\n"
        "Ensure consistency and generality in relationship types when constructing "
        "knowledge graphs. Instead of using specific and momentary types "
        "such as 'BECAME_PROFESSOR', use more general and timeless relationship types "
        "like 'PROFESSOR'. Make sure to use general and timeless relationship types!\n"
        "## 3. Coreference Resolution\n"
        "- **Maintain Entity Consistency**: When extracting entities, it's vital to "
        "ensure consistency.\n"
        'If an entity, such as "John Doe", is mentioned multiple times in the text '
        'but is referred to by different names or pronouns (e.g., "Joe", "he"),'
        "always use the most complete identifier for that entity throughout the "
        'knowledge graph. In this example, use "John Doe" as the entity ID.\n'
        "Remember, the knowledge graph should be coherent and easily understandable, "
        "so maintaining consistency in entity references is crucial.\n"
        "## 4. Strict Compliance\n"
        "Adhere to the rules strictly. Non-compliance will result in termination."
    )

    default_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            system_prompt,
        ),
        (
            "human",
            ("Tip: Make sure to answer in the correct format and do "
             "not include any explanations. "
             "Use the given format to extract information from the "
             "node ID use Chinese, do not change to English"
             "relationships don't only number"
             "following input: {input}"),
        ),
    ])

    return default_prompt
