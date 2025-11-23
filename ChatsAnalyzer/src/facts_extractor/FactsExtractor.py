import re
from enum import Enum

import spacy
from fastcoref import CorefResult
from spacy import Language
from spacy.tokens import Token

from src.facts_extractor.Entity import Entity
from src.facts_extractor.Fact import Fact


class ObjectDependenciesFactDepth(Enum):
    NotIncluded = "NotIncluded"
    DirectChildren = "DirectChildren"
    AllDescendants = "AllDescendants"


class FactsExtractor:
    joined_messages_separator = "|||SPRTR|||"
    entity_counter = 0
    object_dependencies_depth = ObjectDependenciesFactDepth.NotIncluded

    def __init__(self,
                 nlp: Language = spacy.load("en_core_web_trf"),
                 coref_model=None):

        self.nlp = nlp
        self.coref_model = coref_model

    def extract_facts(self, jsnol_entries) -> list[Fact]:
        facts = []
        for entry in jsnol_entries:
            facts += self._extract_facts_from_entry(entry)
        return facts

    def _extract_facts_from_entry(self, entry) -> list[Fact]:
        try:
            input_author, input_text = entry["input"].split(":", 1)
            output_author, output_text = entry["output"].split(":", 1)
        except ValueError:
            return []

        joined = self._join_messages(input_author, input_text, output_author, output_text)
        resolved = self._resolve_coref(joined)
        splitted = self._split_messages(resolved)

        resolved_input, resolved_output = splitted[0], splitted[1]

        input_facts = self._extract_facts_from_text(resolved_input, input_author, output_author)
        output_facts = self._extract_facts_from_text(resolved_output, output_author, input_author)

        return input_facts + output_facts

    def _extract_facts_from_text(self, text, first_person_replacement, second_person_replacement) -> list[Fact]:
        doc = self.nlp(text)
        facts = []

        for token in doc:
            if token.pos_ == "VERB":

                if self._is_question_sentence(token):
                    continue

                subject_text = None
                object_text = None

                auxiliaries = [aux.text for aux in token.children if aux.dep_ in ("aux", "auxpass", "ADV")]
                negations = [neg.lemma_ for neg in token.children if neg.dep_ == "neg"]
                verb_phrase = " ".join(auxiliaries + negations + [token.text])

                for child in token.children:
                    if child.dep_ in ("nsubj", "nsubjpass"):
                        subject_text = self._try_replace_pronoun(child, first_person_replacement,
                                                                 second_person_replacement)
                        if subject_text is not None:
                            subject_text = self._get_entity_text_with_deps(child, subject_text,
                                                                           first_person_replacement,
                                                                           second_person_replacement)

                    elif child.dep_ in ("dobj", "pobj", "attr", "acomp", "xcomp"):
                        object_text = self._try_replace_pronoun(child, first_person_replacement,
                                                                second_person_replacement)
                        if object_text is not None:
                            object_text = self._get_entity_text_with_deps(child, object_text, first_person_replacement,
                                                                          second_person_replacement)

                if subject_text and object_text:
                    FactsExtractor.entity_counter += 1
                    subject = Entity(FactsExtractor.entity_counter, subject_text)
                    FactsExtractor.entity_counter += 1
                    object = Entity(FactsExtractor.entity_counter, object_text)
                    facts.append(Fact(subject, verb_phrase, object))

        return facts

    def _get_entity_text_with_deps(self, token, current_text, first_person_replacement, second_person_replacement):
        object_deps = ""
        match self.object_dependencies_depth:
            case ObjectDependenciesFactDepth.NotIncluded:
                pass
            case ObjectDependenciesFactDepth.DirectChildren:
                object_deps = " ".join(
                    [
                        self._try_replace_pronoun(token, first_person_replacement, second_person_replacement, False)
                        for token in token.children
                    ]
                )
            case ObjectDependenciesFactDepth.AllDescendants:
                object_deps = " ".join(
                    [
                        self._try_replace_pronoun(token, first_person_replacement, second_person_replacement, False)
                        for token in self._get_deps_bfs(token, [])
                    ]
                )

        if object_deps != "":
            current_text = current_text + " " + object_deps
        return current_text

    def _resolve_coref(self, text: str) -> str:
        return text
        # Abandoned as it introduces logical errors to text
        # pred = self.coref_model.predict(texts=[text])
        # #print(pred[0].text)
        # #print(self._get_resolved_text(text, pred[0]))
        # return self._get_resolved_text(text, pred[0])

    def _get_resolved_text(self, original: str, coref_result: CorefResult) -> str:
        result = original
        for cluster in coref_result.get_clusters():
            base = cluster[0]
            for entry in cluster:
                if entry is not base:
                    result = re.sub(rf"\b{re.escape(entry)}\b", base, result)
        return result

    def _join_messages(self, author1, message1, author2, message2) -> str:
        return FactsExtractor.joined_messages_separator.join([author1 + ": " + message1, author2 + ": " + message2])

    def _split_messages(self, message) -> list[str]:
        splitted = message.split(FactsExtractor.joined_messages_separator)
        splitted[0] = splitted[0].split(':', 1)[1]
        splitted[1] = splitted[1].split(':', 1)[1]
        return splitted

    def _try_replace_pronoun(self, token: Token, first_person: str, second_person: str,
                             fail_is_None: bool = True) -> str:
        if token.pos_ != "PRON":
            return token.text

        person = token.morph.get("Person")
        number = token.morph.get("Number")
        if person == ['1']:
            if number == ["Sing"]:
                return first_person
            else:
                return first_person  # + " and " + second_person
        elif person == ['2']:
            return second_person
        else:
            if fail_is_None:
                return None
            else:
                return token.text

    def _add_all_children(self, token, current_text) -> str:

        for child in token.children:
            current_text += child.text + " "

        return current_text

    def _get_deps_bfs(self, token: Token, deps_list=[]) -> list[Token]:
        deps_list += token.children
        for child in token.children:
            self._get_deps_bfs(child, deps_list)

        return [token for token in deps_list if token.pos_ != "DET"]

    def _token_list_to_str(self, token_list):
        result = ""
        for token in token_list:
            result += token.text + " "

        return result.rstrip()

    def _is_question_sentence(self, root_token: Token) -> bool:
        for token in root_token.children:
            if token.text.strip() == "?":
                return True
        return False
