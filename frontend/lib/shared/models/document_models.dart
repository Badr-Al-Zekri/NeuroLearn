class DocumentMetadata {
  const DocumentMetadata({
    required this.documentId,
    required this.title,
    required this.kind,
    required this.wordCount,
    required this.createdAt,
    required this.features,
  });

  final String documentId;
  final String title;
  final String kind;
  final int wordCount;
  final DateTime createdAt;
  final Map<String, bool> features;

  factory DocumentMetadata.fromJson(Map<String, dynamic> json) {
    return DocumentMetadata(
      documentId: json['document_id'] as String,
      title: json['title'] as String,
      kind: json['kind'] as String,
      wordCount: json['word_count'] as int,
      createdAt: DateTime.parse(json['created_at'] as String),
      features: Map<String, bool>.from(json['features'] as Map? ?? {}),
    );
  }
}

class SummaryResult {
  const SummaryResult({
    required this.title,
    required this.overview,
    required this.keyInsights,
    required this.studyActions,
    required this.confidence,
    required this.sourceCoverage,
  });

  final String title;
  final String overview;
  final List<String> keyInsights;
  final List<String> studyActions;
  final double confidence;
  final String sourceCoverage;

  factory SummaryResult.fromJson(Map<String, dynamic> json) {
    return SummaryResult(
      title: json['title'] as String,
      overview: json['overview'] as String,
      keyInsights: List<String>.from(json['key_insights'] as List),
      studyActions: List<String>.from(json['study_actions'] as List),
      confidence: (json['confidence'] as num).toDouble(),
      sourceCoverage: json['source_coverage'] as String,
    );
  }
}

class QuizResult {
  const QuizResult({required this.title, required this.questions});
  final String title;
  final List<QuizQuestion> questions;

  factory QuizResult.fromJson(Map<String, dynamic> json) {
    return QuizResult(
      title: json['title'] as String,
      questions: (json['questions'] as List)
          .map((item) => QuizQuestion.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class QuizQuestion {
  const QuizQuestion({
    required this.id,
    required this.question,
    required this.options,
    required this.correctIndex,
    required this.explanation,
    required this.difficulty,
  });

  final String id;
  final String question;
  final List<String> options;
  final int correctIndex;
  final String explanation;
  final String difficulty;

  factory QuizQuestion.fromJson(Map<String, dynamic> json) {
    return QuizQuestion(
      id: json['id'] as String,
      question: json['question'] as String,
      options: List<String>.from(json['options'] as List),
      correctIndex: json['correct_index'] as int,
      explanation: json['explanation'] as String,
      difficulty: json['difficulty'] as String,
    );
  }
}

class ChatMessage {
  const ChatMessage({required this.role, required this.content});
  final String role;
  final String content;

  Map<String, dynamic> toJson() => {'role': role, 'content': content};
}

class ChatAnswer {
  const ChatAnswer({required this.answer, required this.citedInsights});
  final String answer;
  final List<String> citedInsights;

  factory ChatAnswer.fromJson(Map<String, dynamic> json) {
    return ChatAnswer(
      answer: json['answer'] as String,
      citedInsights: List<String>.from(json['cited_insights'] as List? ?? []),
    );
  }
}

class StudySession {
  const StudySession({
    required this.sessionId,
    required this.learnerId,
    required this.documentIds,
    required this.durationSeconds,
    required this.quizAttempts,
    required this.quizAccuracy,
    required this.retrievalInteractions,
    required this.chatTurns,
    required this.engagementScore,
    required this.ended,
  });

  final String sessionId;
  final String learnerId;
  final List<String> documentIds;
  final int durationSeconds;
  final int quizAttempts;
  final double quizAccuracy;
  final int retrievalInteractions;
  final int chatTurns;
  final double engagementScore;
  final bool ended;

  factory StudySession.fromJson(Map<String, dynamic> json) {
    return StudySession(
      sessionId: json['session_id'] as String,
      learnerId: json['learner_id'] as String,
      documentIds: List<String>.from(json['document_ids'] as List? ?? []),
      durationSeconds: json['duration_seconds'] as int? ?? 0,
      quizAttempts: json['quiz_attempts'] as int? ?? 0,
      quizAccuracy: (json['quiz_accuracy'] as num? ?? 0).toDouble(),
      retrievalInteractions: json['retrieval_interactions'] as int? ?? 0,
      chatTurns: json['chat_turns'] as int? ?? 0,
      engagementScore: (json['engagement_score'] as num? ?? 0).toDouble(),
      ended: json['ended_at'] != null,
    );
  }
}

class RecommendationSummary {
  const RecommendationSummary({
    required this.title,
    required this.rationale,
    required this.priority,
    this.conceptId,
  });

  final String title;
  final String rationale;
  final double priority;
  final String? conceptId;

  factory RecommendationSummary.fromJson(Map<String, dynamic> json) {
    return RecommendationSummary(
      title: json['title'] as String,
      rationale: json['rationale'] as String,
      priority: (json['priority'] as num? ?? 0.5).toDouble(),
      conceptId: json['concept_id'] as String?,
    );
  }
}

class AdaptiveDecisionSummary {
  const AdaptiveDecisionSummary({
    required this.tutoringMode,
    required this.pacing,
    required this.recommendations,
    required this.revisionCount,
    required this.nextAction,
  });

  final String tutoringMode;
  final String pacing;
  final List<RecommendationSummary> recommendations;
  final int revisionCount;
  final String nextAction;

  factory AdaptiveDecisionSummary.fromJson(Map<String, dynamic> json) {
    final strategy = json['tutoring_strategy'] as Map<String, dynamic>? ?? {};
    final load = json['cognitive_load'] as Map<String, dynamic>? ?? {};
    final path = json['learning_path'] as Map<String, dynamic>? ?? {};
    return AdaptiveDecisionSummary(
      tutoringMode: strategy['mode'] as String? ?? 'beginner',
      pacing: load['pacing_adjustment'] as String? ?? 'normal',
      nextAction: path['next_action'] as String? ?? 'continue_current',
      revisionCount: (json['revision_priorities'] as List? ?? const []).length,
      recommendations: (json['ranked_recommendations'] as List? ?? const [])
          .map((item) => RecommendationSummary.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}

class LearnerSnapshot {
  const LearnerSnapshot({
    required this.completedSessions,
    required this.masteryCount,
    required this.weakConceptCount,
    required this.activeSessionCount,
    required this.recommendations,
  });

  final int completedSessions;
  final int masteryCount;
  final int weakConceptCount;
  final int activeSessionCount;
  final List<RecommendationSummary> recommendations;

  factory LearnerSnapshot.fromJson(Map<String, dynamic> json) {
    final memory = json['memory'] as Map<String, dynamic>? ?? {};
    final weakness = json['weakness_profile'] as Map<String, dynamic>? ?? {};
    final recommendations = json['recommendations'] as Map<String, dynamic>? ?? {};
    final sessionIds = memory['session_ids'] as List? ?? const [];
    return LearnerSnapshot(
      completedSessions: sessionIds.length,
      masteryCount: (json['mastery'] as List? ?? const []).length,
      weakConceptCount: (weakness['weak_concept_ids'] as List? ?? const []).length,
      activeSessionCount: (json['active_sessions'] as List? ?? const []).length,
      recommendations: (recommendations['recommendations'] as List? ?? const [])
          .map((item) => RecommendationSummary.fromJson(item as Map<String, dynamic>))
          .toList(),
    );
  }
}
