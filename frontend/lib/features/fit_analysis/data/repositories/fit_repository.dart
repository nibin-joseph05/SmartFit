import 'dart:io';
import '../../domain/entities/fit_result.dart';
import '../datasources/fit_remote_datasource.dart';

class FitRepository {
  final FitRemoteDataSource remoteDataSource;

  FitRepository(this.remoteDataSource);

  Future<FitResult> analyzeFit({
    required File personImage,
    required File garmentImage,
  }) async {
    return await remoteDataSource.analyzeFit(
      personImage: personImage,
      garmentImage: garmentImage,
    );
  }
}
