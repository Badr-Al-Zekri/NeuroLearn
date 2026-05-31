from datetime import datetime, timezone
from uuid import uuid4
from app.models.learner import ConceptMastery, LearnerProfile, LearningMemory, StudySession


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class LearnerStore:
    def __init__(self) -> None:
        self._profiles: dict[str, LearnerProfile] = {}
        self._memory: dict[str, LearningMemory] = {}
        self._mastery: dict[str, dict[str, ConceptMastery]] = {}
        self._sessions: dict[str, dict[str, StudySession]] = {}

    def get_or_create_profile(self, learner_id: str, display_name: str | None = None) -> LearnerProfile:
        profile = self._profiles.get(learner_id)
        if profile:
            return profile
        now = utc_now()
        profile = LearnerProfile(
            learner_id=learner_id,
            display_name=display_name or "Demo Learner",
            created_at=now,
            updated_at=now,
        )
        self._profiles[learner_id] = profile
        self._memory[learner_id] = LearningMemory(learner_id=learner_id, updated_at=now)
        self._mastery[learner_id] = {}
        self._sessions[learner_id] = {}
        return profile

    def get_memory(self, learner_id: str) -> LearningMemory:
        self.get_or_create_profile(learner_id)
        return self._memory[learner_id]

    def save_memory(self, memory: LearningMemory) -> LearningMemory:
        self._memory[memory.learner_id] = memory.model_copy(update={"updated_at": utc_now()})
        return self._memory[memory.learner_id]

    def get_mastery(self, learner_id: str, concept_id: str, concept_name: str) -> ConceptMastery:
        self.get_or_create_profile(learner_id)
        mastery_map = self._mastery[learner_id]
        if concept_id not in mastery_map:
            mastery_map[concept_id] = ConceptMastery(learner_id=learner_id, concept_id=concept_id, concept_name=concept_name)
        return mastery_map[concept_id]

    def save_mastery(self, mastery: ConceptMastery) -> ConceptMastery:
        self.get_or_create_profile(mastery.learner_id)
        self._mastery[mastery.learner_id][mastery.concept_id] = mastery
        return mastery

    def list_mastery(self, learner_id: str) -> list[ConceptMastery]:
        self.get_or_create_profile(learner_id)
        return list(self._mastery[learner_id].values())

    def create_session(self, learner_id: str, document_ids: list[str]) -> StudySession:
        self.get_or_create_profile(learner_id)
        session = StudySession(
            session_id=str(uuid4()),
            learner_id=learner_id,
            document_ids=document_ids,
            started_at=utc_now(),
        )
        self._sessions[learner_id][session.session_id] = session
        memory = self.get_memory(learner_id)
        session_ids = [*memory.session_ids, session.session_id]
        self.save_memory(memory.model_copy(update={"session_ids": session_ids}))
        return session

    def get_session(self, learner_id: str, session_id: str) -> StudySession | None:
        self.get_or_create_profile(learner_id)
        return self._sessions[learner_id].get(session_id)

    def save_session(self, session: StudySession) -> StudySession:
        self.get_or_create_profile(session.learner_id)
        self._sessions[session.learner_id][session.session_id] = session
        return session

    def list_sessions(self, learner_id: str) -> list[StudySession]:
        self.get_or_create_profile(learner_id)
        return list(self._sessions[learner_id].values())


learner_store = LearnerStore()

