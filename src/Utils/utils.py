from crewai.knowledge.source.string_knowledge_source import StringKnowledgeSource
from crewai.knowledge.source.crew_docling_source import CrewDoclingSource
from crewai.knowledge.source.json_knowledge_source import JSONKnowledgeSource

def get_knowledge_type(input_file_path:str):        
    if not input_file_path:
        return "Error: No input file provided."
    
    # Handle JSON input
    if input_file_path.endswith(".json"):
        return JSONKnowledgeSource(file_paths=[input_file_path])

    # Handle TXT input
    elif input_file_path.endswith(".txt"):
        try:
            with open(input_file_path, "r", encoding="utf-8") as file:
                return StringKnowledgeSource(content=file.read())
        except FileNotFoundError:
            return f"Error: File '{input_file_path}' not found."
        except Exception as e:
            return f"Error reading file: {e}"
                    
    # Unsupported file type
    else:
        return "Error: Unsupported file format. Please provide a .txt or .json file."
