import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:neurolearn_ai/core/widgets/app_shell.dart';
import 'package:neurolearn_ai/features/practice/presentation/practice_screen.dart';
import 'package:neurolearn_ai/features/progress/presentation/progress_screen.dart';
import 'package:neurolearn_ai/features/today/presentation/today_screen.dart';
import 'package:neurolearn_ai/features/tutor/presentation/tutor_screen.dart';
import 'package:neurolearn_ai/features/upload/presentation/upload_screen.dart';

final routerProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      ShellRoute(
        builder: (context, state, child) => AppShell(child: child),
        routes: [
          GoRoute(path: '/', builder: (_, __) => const TodayScreen()),
          GoRoute(path: '/tutor', builder: (_, __) => const TutorScreen()),
          GoRoute(path: '/practice', builder: (_, __) => const PracticeScreen()),
          GoRoute(path: '/progress', builder: (_, __) => const ProgressScreen()),
          GoRoute(path: '/upload', builder: (_, __) => const UploadScreen()),
        ],
      ),
    ],
  );
});
