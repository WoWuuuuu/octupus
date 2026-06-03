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
        intent_type = self._classify_intent(content, context)
        parsed = self._parse_content(content, intent_type)
        entities = self._extract_entities(content)
        
        return Intent(
            intent_id=f"intent_{datetime.now().timestamp()}",
            intent_type=intent_type,
            raw_content=content,
            parsed_content=parsed,
            entities=entities,
            context=context or {},
        )
    
    def _classify_intent(
        self, 
        content: str, 
        context: Optional[Dict[str, Any]]
    ) -> IntentType:
        content_lower = content.lower()
        
        if context and context.get("source"):
            source = context["source"]
            if source == "webhook":
                return IntentType.EXTERNAL_SIGNAL
            elif source == "scheduler":
                return IntentType.SCHEDULED_TASK
            elif source == "monitor":
                return IntentType.MONITORING_ALERT
        
        if any(kw in content_lower for kw in ["error", "failed", "exception", "crash"]):
            return IntentType.ERROR_OBSERVATION
        if any(kw in content_lower for kw in ["what", "how", "why", "where", "when"]):
            return IntentType.QUERY
        if any(kw in content_lower for kw in ["do", "execute", "run", "create", "delete", "update"]):
            return IntentType.COMMAND
        if any(kw in content_lower for kw in ["please", "can you", "i want", "need"]):
            return IntentType.USER_REQUEST
        
        return IntentType.UNKNOWN
    
    def _parse_content(self, content: str, intent_type: IntentType) -> Dict[str, Any]:
        parsed = {
            "original": content,
            "tokens": self._tokenize(content),
            "intent_type": intent_type.value,
        }
        
        if intent_type == IntentType.COMMAND:
            parsed["action"] = self._extract_action(content)
            parsed["target"] = self._extract_target(content)
            parsed["parameters"] = self._extract_parameters(content)
        
        return parsed
    
    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r'\w+', text.lower())
    
    def _extract_action(self, content: str) -> Optional[str]:
        actions = ["create", "read", "update", "delete", "execute", "run", "send", "fetch"]
        tokens = self._tokenize(content)
        for token in tokens:
            if token in actions:
                return token
        return None
    
    def _extract_target(self, content: str) -> Optional[str]:
        targets = ["file", "database", "api", "service", "user", "config", "report"]
        tokens = self._tokenize(content)
        for token in tokens:
            if token in targets:
                return token
        return None
    
    def _extract_parameters(self, content: str) -> Dict[str, Any]:
        params = {}
        param_pattern = r'(\w+)=["\']([^"\']+)["\']'
        matches = re.findall(param_pattern, content)
        for key, value in matches:
            params[key] = value
        return params
    
    def _extract_entities(self, content: str) -> List[str]:
        entities = []
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        url_pattern = r'https?://[^\s]+'
        path_pattern = r'[A-Za-z]:\\[^\s]+|/[^\s]+'
        
        entities.extend(re.findall(email_pattern, content))
        entities.extend(re.findall(url_pattern, content))
        entities.extend(re.findall(path_pattern, content))
        
        return entities


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
