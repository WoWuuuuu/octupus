"""
Perception Module - Intent perception and interpretation for Octopus Decision Layer

Processes raw input signals and extracts meaningful information for decision making.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Callable
from datetime import datetime
from enum import Enum
import re


class IntentType(Enum):
    USER_REQUEST = "user_request"
    SYSTEM_EVENT = "system_event"
    EXTERNAL_SIGNAL = "external_signal"
    SCHEDULED_TASK = "scheduled_task"
    MONITORING_ALERT = "monitoring_alert"
    QUERY = "query"
    COMMAND = "command"
    QUERY_RESPONSE = "query_response"
    ERROR_OBSERVATION = "error_observation"
    UNKNOWN = "unknown"


class SignalSource(Enum):
    USER = "user"
    API = "api"
    WEBHOOK = "webhook"
    SCHEDULER = "scheduler"
    MONITOR = "monitor"
    AGENT = "agent"
    EXTERNAL = "external"
    INTERNAL = "internal"


@dataclass
class Intent:
    intent_id: str
    intent_type: IntentType
    raw_content: str
    parsed_content: Dict[str, Any]
    entities: List[str] = field(default_factory=list)
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.now)
    source: SignalSource = SignalSource.USER
    context: Dict[str, Any] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    priority: int = 3
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "intent_type": self.intent_type.value,
            "raw_content": self.raw_content,
            "parsed_content": self.parsed_content,
            "entities": self.entities,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source.value,
            "context": self.context,
            "constraints": self.constraints,
            "priority": self.priority,
            "metadata": self.metadata,
        }


@dataclass
class PerceptionResult:
    intents: List[Intent]
    extracted_entities: Dict[str, Any]
    contextual_info: Dict[str, Any]
    confidence: float
    processing_time_ms: float
    timestamp: datetime = field(default_factory=datetime.now)
    raw_signals: List[Any] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "intents": [i.to_dict() for i in self.intents],
            "extracted_entities": self.extracted_entities,
            "contextual_info": self.contextual_info,
            "confidence": self.confidence,
            "processing_time_ms": self.processing_time_ms,
            "timestamp": self.timestamp.isoformat(),
        }


import json
from core.llm_client import llm

class IntentParser:
    def __init__(self):
        self.patterns: Dict[IntentType, List[Callable]] = {}
        self.entity_extractors: Dict[str, Callable] = {}
    
    def register_pattern(self, intent_type: IntentType, parser: Callable):
        if intent_type not in self.patterns:
            self.patterns[intent_type] = []
        self.patterns[intent_type].append(parser)
    
    def register_entity_extractor(self, entity_type: str, extractor: Callable):
        self.entity_extractors[entity_type] = extractor
    
    def parse(self, content: str, context: Optional[Dict[str, Any]] = None) -> Intent:
        # Prompt the LLM for intent extraction using JSON mode
        system_prompt = f"""
You are the Perception Module of the Octopus Decision Engine.
Your job is to parse raw input and extract the user's intent into a structured JSON object.

Valid IntentTypes: {[t.value for t in IntentType]}

You must return ONLY a JSON object with this exact structure:
{{
    "intent_type": "<one of the Valid IntentTypes>",
    "parsed_content": {{"action": "...", "target": "...", "parameters": {{}}}},
    "entities": ["list of entities like emails, URLs, file paths, IDs"],
    "confidence": 0.95
}}
"""
        try:
            response = llm.chat(
                prompt=f"Raw Input: {content}\nContext: {context}", 
                system_prompt=system_prompt,
                json_mode=True
            )
            parsed_data = json.loads(response)
            
            # Map string intent_type back to Enum safely
            intent_str = parsed_data.get("intent_type", "unknown")
            try:
                intent_type = IntentType(intent_str)
            except ValueError:
                intent_type = IntentType.UNKNOWN
                
            parsed_content = parsed_data.get("parsed_content", {"original": content})
            entities = parsed_data.get("entities", [])
            confidence = float(parsed_data.get("confidence", 0.8))
            
        except Exception as e:
            # Fallback to simple heuristic if LLM fails (e.g. mock mode without JSON support)
            print(f"[Perception] LLM intent extraction failed: {e}. Falling back to heuristics.")
            intent_type = self._fallback_classify(content)
            parsed_content = {"original": content, "error": str(e)}
            entities = []
            confidence = 0.5
            
        return Intent(
            intent_id=f"intent_{datetime.now().timestamp()}",
            intent_type=intent_type,
            raw_content=content,
            parsed_content=parsed_content,
            entities=entities,
            confidence=confidence,
            context=context or {},
        )
        
    def _fallback_classify(self, content: str) -> IntentType:
        content_lower = content.lower()
        if any(kw in content_lower for kw in ["error", "failed", "crash"]): return IntentType.ERROR_OBSERVATION
        if any(kw in content_lower for kw in ["what", "how", "why"]): return IntentType.QUERY
        if any(kw in content_lower for kw in ["do", "execute", "run"]): return IntentType.COMMAND
        return IntentType.USER_REQUEST



class PerceptionModule:
    def __init__(self):
        self.intent_parser = IntentParser()
        self.sensors: Dict[str, Callable] = {}
        self.context_providers: List[Callable] = []
        self.perception_history: List[PerceptionResult] = []
    
    def register_sensor(self, name: str, sensor: Callable):
        self.sensors[name] = sensor
    
    def register_context_provider(self, provider: Callable):
        self.context_providers.append(provider)
    
    def perceive(self, raw_input: Any) -> PerceptionResult:
        start_time = datetime.now()
        
        signals = self._collect_signals(raw_input)
        intents = self._process_signals(signals)
        entities = self._aggregate_entities(intents)
        contextual_info = self._build_context()
        
        confidence = self._calculate_confidence(intents)
        
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        result = PerceptionResult(
            intents=intents,
            extracted_entities=entities,
            contextual_info=contextual_info,
            confidence=confidence,
            processing_time_ms=processing_time,
            raw_signals=signals,
        )
        
        self.perception_history.append(result)
        return result
    
    def _collect_signals(self, raw_input: Any) -> List[Any]:
        signals = []
        
        if isinstance(raw_input, list):
            signals.extend(raw_input)
        elif isinstance(raw_input, dict):
            signals.append(raw_input)
        else:
            signals.append({"content": str(raw_input)})
        
        return signals
    
    def _process_signals(self, signals: List[Any]) -> List[Intent]:
        intents = []
        
        for signal in signals:
            content = self._extract_content(signal)
            context = self._extract_context(signal)
            
            intent = self.intent_parser.parse(content, context)
            intents.append(intent)
        
        return intents
    
    def _extract_content(self, signal: Any) -> str:
        if isinstance(signal, dict):
            return signal.get("content", str(signal))
        return str(signal)
    
    def _extract_context(self, signal: Any) -> Dict[str, Any]:
        if isinstance(signal, dict):
            context = signal.get("context", {})
            if "source" in signal:
                context["source"] = signal["source"]
            return context
        return {}
    
    def _aggregate_entities(self, intents: List[Intent]) -> Dict[str, Any]:
        all_entities = {}
        for intent in intents:
            all_entities[intent.intent_id] = {
                "entities": intent.entities,
                "type": intent.intent_type.value,
                "confidence": intent.confidence,
            }
        return all_entities
    
    def _build_context(self) -> Dict[str, Any]:
        context = {}
        
        for provider in self.context_providers:
            try:
                context.update(provider())
            except Exception:
                pass
        
        return context
    
    def _calculate_confidence(self, intents: List[Intent]) -> float:
        if not intents:
            return 0.0
        
        total_confidence = sum(intent.confidence for intent in intents)
        return total_confidence / len(intents)
    
    def get_perception_summary(self) -> Dict[str, Any]:
        return {
            "total_perceptions": len(self.perception_history),
            "recent_intents": [
                i.intent_type.value for i in self.perception_history[-5:]
            ],
            "entity_types": list(set(
                e for r in self.perception_history 
                for e in r.extracted_entities.keys()
            )),
        }
