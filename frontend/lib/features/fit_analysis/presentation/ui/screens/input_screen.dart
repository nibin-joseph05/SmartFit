import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../providers/fit_provider.dart';
import 'result_screen.dart';

class InputScreen extends ConsumerStatefulWidget {
  const InputScreen({super.key});

  @override
  ConsumerState<InputScreen> createState() => _InputScreenState();
}

class _InputScreenState extends ConsumerState<InputScreen> {
  final _heightController = TextEditingController();
  final _weightController = TextEditingController();
  String _selectedDress = "Shirt";
  File? _selectedImage;

  Future<void> _pickImage() async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        _selectedImage = File(pickedFile.path);
      });
    }
  }

  void _submit() async {
    if (_selectedImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select an image')),
      );
      return;
    }

    final height = double.tryParse(_heightController.text) ?? 0;
    final weight = double.tryParse(_weightController.text) ?? 0;

    if (height <= 0 || weight <= 0) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please enter valid height and weight')),
      );
      return;
    }

    await ref.read(fitProvider.notifier).analyzeFit(
          height: height,
          weight: weight,
          dressType: _selectedDress,
          imageFile: _selectedImage!,
        );

    if (mounted) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const ResultScreen()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("SmartFit AI")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextField(
              controller: _heightController,
              decoration: const InputDecoration(labelText: "Height (cm)"),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _weightController,
              decoration: const InputDecoration(labelText: "Weight (kg)"),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            DropdownButtonFormField<String>(
              initialValue: _selectedDress,
              items: ["Shirt", "T-Shirt", "Dress", "Suit"]
                  .map((e) => DropdownMenuItem(value: e, child: Text(e)))
                  .toList(),
              onChanged: (val) {
                if (val != null) setState(() => _selectedDress = val);
              },
              decoration: const InputDecoration(labelText: "Dress Type"),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              icon: const Icon(Icons.image),
              label: Text(_selectedImage == null ? "Upload Photo" : "Photo Selected"),
              onPressed: _pickImage,
            ),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: ref.watch(fitProvider).isLoading ? null : _submit,
              child: ref.watch(fitProvider).isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text("Check My Fit"),
            ),
          ],
        ),
      ),
    );
  }
}
