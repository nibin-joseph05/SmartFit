import 'dart:io';
import '../../domain/entities/fit_result.dart';
import '../datasources/fit_remote_datasource.dart';

class FitRepository {
  final FitRemoteDataSource remoteDataSource;

  FitRepository(this.remoteDataSource);

  Future<FitResult> analyzeFit({
    required double height,
    required double weight,
    required String dressType,
    required File imageFile,
  }) async {
    return await remoteDataSource.analyzeFit(
      height: height,
      weight: weight,
      dressType: dressType,
      imageFile: imageFile,
    );
  }
}
