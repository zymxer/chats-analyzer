import json

from fastapi import APIRouter, UploadFile, File

from src.facts_extractor.FactsExtractor import FactsExtractor, ObjectDependenciesFactDepth

router = APIRouter()
factsExtractor = FactsExtractor()


@router.post("/extract-from/file",
             summary="Extract facts from provided .jsnol file",
             response_description="Array of facts in (subject, action, object) format",
             response_model=list[str]
             )
async def extract_facts_from_file(
        jsonl: UploadFile = File(...)
):
    bytes = await jsonl.read()
    text = bytes.decode("utf-8")
    lines = text.splitlines()
    data = [json.loads(line) for line in lines]
    facts = factsExtractor.extract_facts(data)
    return [str(fact) for fact in facts]

@router.post("/extract-from/str",
             summary="Extract facts from provided .jsnol-like string",
             response_description="Array of facts in (subject, action, object) format"
             )
def extract_facts_from_str(
        text: str
):
    lines = text.splitlines()
    data = [json.loads(line) for line in lines]
    facts = factsExtractor.extract_facts(data)
    return [str(fact) for fact in facts]

@router.post("/cfg-deps-depth",
             summary="Sets object dependencies depth of facts extractor",
             description="Available values are NotIncluded, DirectChildren, AllDescendants",)
def set_object_dependencies_depth(
        depth: ObjectDependenciesFactDepth
):
    FactsExtractor.object_dependencies_depth = depth.value