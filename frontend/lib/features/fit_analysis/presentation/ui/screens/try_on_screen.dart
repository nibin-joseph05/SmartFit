import 'dart:io';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:image_picker/image_picker.dart';
import '../../providers/fit_provider.dart';
import 'result_screen.dart';

class TryOnScreen extends ConsumerStatefulWidget {
  const TryOnScreen({super.key});

  @override
  ConsumerState<TryOnScreen> createState() => _TryOnScreenState();
}

class _TryOnScreenState extends ConsumerState<TryOnScreen> {
  File? _personImage;
  File? _garmentImage;

  Future<void> _pickImage(bool isPerson) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: ImageSource.gallery);
    if (pickedFile != null) {
      setState(() {
        if (isPerson) {
          _personImage = File(pickedFile.path);
        } else {
          _garmentImage = File(pickedFile.path);
        }
      });
    }
  }

  void _submit() async {
    if (_personImage == null || _garmentImage == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please select both your photo and the garment photo')),
      );
      return;
    }

    await ref.read(fitProvider.notifier).analyzeFit(
          personImage: _personImage!,
          garmentImage: _garmentImage!,
        );

    if (mounted && ref.read(fitProvider).hasValue && !ref.read(fitProvider).hasError) {
      Navigator.push(
        context,
        MaterialPageRoute(builder: (_) => const ResultScreen()),
      );
    } else if (mounted && ref.read(fitProvider).hasError) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: ${ref.read(fitProvider).error}')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final isLoading = ref.watch(fitProvider).isLoading;

    return Scaffold(
      appBar: AppBar(title: const Text("Virtual Try-On")),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text("Upload Images", style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold)),
            const SizedBox(height: 20),
            _buildImagePicker("Your Photo", _personImage, () => _pickImage(true)),
            const SizedBox(height: 20),
            _buildImagePicker("Garment Photo", _garmentImage, () => _pickImage(false)),
            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: isLoading ? null : _submit,
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.all(16)),
              child: isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text("Generate Virtual Try-On", style: TextStyle(fontSize: 18)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildImagePicker(String label, File? image, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        height: 200,
        decoration: BoxDecoration(
          color: Colors.grey.shade100,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: Colors.grey.shade300, width: 2),
        ),
        child: image != null
            ? ClipRRect(
                borderRadius: BorderRadius.circular(10),
                child: Image.file(image, fit: BoxFit.cover),
              )
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.add_a_photo, size: 40, color: Colors.blueAccent),
                  const SizedBox(height: 10),
                  Text(label, style: const TextStyle(fontSize: 16)),
                ],
              ),
      ),
    );
  }
}
