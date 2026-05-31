import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:neurolearn_ai/core/api/api_client.dart';
import 'package:neurolearn_ai/shared/models/document_models.dart';
import 'package:neurolearn_ai/shared/providers/document_provider.dart';
import 'package:neurolearn_ai/shared/providers/telemetry_provider.dart';

const demoLearnerId = 'demo-learner';

final activeStudySessionProvider = StateNotifierProvider<StudySessionController, AsyncValue<StudySession?>>((ref) {
  return StudySessionController(ref);
});

final adaptiveDecisionProvider = FutureProvider.autoDispose<AdaptiveDecisionSummary>((ref) {
  return ref.watch(apiClientProvider).adaptiveDecision(demoLearnerId);
});

final learnerSnapshotProvider = FutureProvider.autoDispose<LearnerSnapshot>((ref) {
  return ref.watch(apiClientProvider).learnerSnapshot(demoLearnerId);
});

class StudySessionController extends StateNotifier<AsyncValue<StudySession?>> {
  StudySessionController(this._ref) : super(const AsyncData(null));
  final Ref _ref;

  Future<void> start() async {
    final document = _ref.read(selectedDocumentProvider);
    if (document == null) {
      return;
    }
    state = const AsyncLoading();
    state = await AsyncValue.guard(() async {
      final session = await _ref.read(apiClientProvider).startStudySession(demoLearnerId, [document.documentId]);
      _ref.read(telemetryProvider.notifier).track('session_started', {'document_id': document.documentId});
      return session;
    });
  }

  Future<void> recordTutorInteraction() async {
    _ref.read(telemetryProvider.notifier).track('tutor_engagement', {});
    try {
      await _record(eventType: 'chat');
    } catch (_) {
      // A delivered explanation remains useful even if session recording is delayed.
    }
  }

  Future<void> recordQuizAnswer({
    required String conceptId,
    required String conceptName,
    required bool correct,
  }) async {
    await _record(eventType: 'quiz_attempt', conceptId: conceptId, conceptName: conceptName, correct: correct);
  }

  Future<void> completeQuiz(int correct, int total) async {
    _ref.read(telemetryProvider.notifier).track('quiz_completed', {'correct': correct, 'total': total});
  }

  Future<void> complete() async {
    final session = state.valueOrNull;
    if (session == null) {
      return;
    }
    state = const AsyncLoading<StudySession?>().copyWithPrevious(AsyncData(session));
    final result = await AsyncValue.guard(() async {
      final ended = await _ref.read(apiClientProvider).endStudySession(demoLearnerId, session.sessionId);
      _ref.read(telemetryProvider.notifier).track('session_completed', {'duration_seconds': ended.durationSeconds});
      return ended;
    });
    state = result.hasError ? result.copyWithPrevious(AsyncData(session)) : result;
  }

  Future<void> leaveForNewMaterial() async {
    final session = state.valueOrNull;
    if (session == null || session.ended) {
      state = const AsyncData(null);
      return;
    }
    _ref.read(telemetryProvider.notifier).trackDropOff(
          'material_changed',
          documentId: session.documentIds.isEmpty ? null : session.documentIds.first,
        );
    state = const AsyncData(null);
    try {
      await _ref.read(apiClientProvider).endStudySession(demoLearnerId, session.sessionId);
    } catch (_) {
      // Changing material should never strand the learner in the upload flow.
    }
  }

  Future<void> _record({
    required String eventType,
    String? conceptId,
    String? conceptName,
    bool? correct,
  }) async {
    var session = state.valueOrNull;
    final document = _ref.read(selectedDocumentProvider);
    if ((session == null || session.ended) && document != null) {
      await start();
      session = state.valueOrNull;
    }
    if (session == null) {
      return;
    }
    final updated = await _ref.read(apiClientProvider).recordStudyEvent(
          demoLearnerId,
          session.sessionId,
          eventType: eventType,
          documentId: document?.documentId,
          conceptId: conceptId,
          conceptName: conceptName,
          correct: correct,
        );
    state = AsyncData(updated);
  }
}
