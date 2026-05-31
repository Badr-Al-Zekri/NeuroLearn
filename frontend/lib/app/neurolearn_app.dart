import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:neurolearn_ai/app/router.dart';
import 'package:neurolearn_ai/app/theme.dart';

class NeuroLearnApp extends ConsumerWidget {
  const NeuroLearnApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(routerProvider);
    return MaterialApp.router(
      title: 'NeuroLearn AI',
      debugShowCheckedModeBanner: false,
      theme: buildNeuroLearnTheme(),
      routerConfig: router,
    );
  }
}

