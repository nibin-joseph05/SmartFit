import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../provider/fit_provider.dart';
import 'result_screen.dart';

class InputScreen extends ConsumerWidget {
  const InputScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final heightController = TextEditingController();
    final weightController = TextEditingController();

    return Scaffold(
      appBar: AppBar(title: const Text("SmartFit AI")),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            TextField(
              controller: heightController,
              decoration: const InputDecoration(labelText: "Height (cm)"),
            ),
            TextField(
              controller: weightController,
              decoration: const InputDecoration(labelText: "Weight (kg)"),
            ),
            const SizedBox(height: 20),
            ElevatedButton(
              onPressed: () async {
                final data = {
                  "height": double.parse(heightController.text),
                  "weight": double.parse(weightController.text),
                };

                await ref.read(fitProvider.notifier).getFit(data);

                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (_) => const ResultScreen(),
                  ),
                );
              },
              child: const Text("Check My Fit"),
            )
          ],
        ),
      ),
    );
  }
}