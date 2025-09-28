import os
import asyncio
from typing import List, Dict, Any, Optional, Callable
from concurrent.futures import ThreadPoolExecutor
from .audio_processor import AudioProcessor

class BatchProcessor:
    """Handle batch processing of multiple audio files"""
    
    def __init__(self):
        self.audio_processor = AudioProcessor()
        self.max_workers = 4  # Limit concurrent processing
    
    async def process_multiple_files(
        self,
        file_paths: List[str],
        operations: List[Dict[str, Any]],
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, Any]:
        """
        Process multiple files with given operations
        
        Args:
            file_paths: List of file paths to process
            operations: List of operations to perform
            progress_callback: Optional callback for progress updates
        
        Returns:
            Dictionary with results and statistics
        """
        results = {
            'successful': [],
            'failed': [],
            'total_files': len(file_paths),
            'operations_applied': len(operations)
        }
        
        # Use ThreadPoolExecutor for CPU-bound tasks
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            tasks = []
            
            for i, file_path in enumerate(file_paths):
                task = asyncio.get_event_loop().run_in_executor(
                    executor,
                    self._process_single_file,
                    file_path,
                    operations,
                    i + 1,
                    len(file_paths)
                )
                tasks.append(task)
            
            # Process files and update progress
            for i, task in enumerate(asyncio.as_completed(tasks)):
                try:
                    result = await task
                    
                    if result['success']:
                        results['successful'].append(result)
                    else:
                        results['failed'].append(result)
                    
                    # Call progress callback if provided
                    if progress_callback:
                        progress = (i + 1) / len(file_paths) * 100
                        await progress_callback(progress, result)
                        
                except Exception as e:
                    results['failed'].append({
                        'file_path': file_paths[i] if i < len(file_paths) else 'unknown',
                        'error': str(e),
                        'success': False
                    })
        
        return results
    
    def _process_single_file(
        self,
        file_path: str,
        operations: List[Dict[str, Any]],
        current_index: int,
        total_files: int
    ) -> Dict[str, Any]:
        """Process a single file with given operations"""
        result = {
            'file_path': file_path,
            'original_name': os.path.basename(file_path),
            'success': True,
            'operations_completed': [],
            'operations_failed': [],
            'output_path': None,
            'error': None
        }
        
        try:
            current_path = file_path
            
            for operation in operations:
                op_type = operation.get('type')
                op_params = operation.get('params', {})
                
                if op_type == 'update_metadata':
                    success = self.audio_processor.update_metadata(current_path, op_params)
                    if success:
                        result['operations_completed'].append(operation)
                    else:
                        result['operations_failed'].append(operation)
                
                elif op_type == 'add_cover':
                    cover_data = op_params.get('cover_data')
                    mime_type = op_params.get('mime_type', 'image/jpeg')
                    success = self.audio_processor.add_cover_art(current_path, cover_data, mime_type)
                    if success:
                        result['operations_completed'].append(operation)
                    else:
                        result['operations_failed'].append(operation)
                
                elif op_type == 'remove_cover':
                    success = self.audio_processor.remove_cover_art(current_path)
                    if success:
                        result['operations_completed'].append(operation)
                    else:
                        result['operations_failed'].append(operation)
                
                elif op_type == 'convert_format':
                    target_format = op_params.get('format')
                    bitrate = op_params.get('bitrate')
                    output_dir = op_params.get('output_dir', os.path.dirname(current_path))
                    
                    base_name = os.path.splitext(os.path.basename(current_path))[0]
                    output_path = os.path.join(output_dir, f"{base_name}.{target_format}")
                    
                    success = self.audio_processor.convert_format(
                        current_path, output_path, target_format, bitrate
                    )
                    
                    if success:
                        current_path = output_path
                        result['output_path'] = output_path
                        result['operations_completed'].append(operation)
                    else:
                        result['operations_failed'].append(operation)
                
                elif op_type == 'rename_file':
                    template = op_params.get('template', '{artist} - {title}')
                    output_dir = op_params.get('output_dir', os.path.dirname(current_path))
                    
                    # Get current metadata
                    metadata = self.audio_processor.get_metadata(current_path)
                    
                    # Generate new filename
                    new_filename = self.audio_processor.generate_filename(metadata, template)
                    extension = os.path.splitext(current_path)[1]
                    new_path = os.path.join(output_dir, f"{new_filename}{extension}")
                    
                    # Copy/move file
                    try:
                        import shutil
                        shutil.copy2(current_path, new_path)
                        current_path = new_path
                        result['output_path'] = new_path
                        result['operations_completed'].append(operation)
                    except Exception as e:
                        result['operations_failed'].append({**operation, 'error': str(e)})
            
            # Set final output path if not set
            if not result['output_path']:
                result['output_path'] = current_path
            
            # Check if any operations failed
            if result['operations_failed']:
                result['success'] = False
                result['error'] = f"Some operations failed: {len(result['operations_failed'])}"
        
        except Exception as e:
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def create_batch_operations(
        self,
        metadata_updates: Optional[Dict[str, str]] = None,
        cover_action: Optional[Dict[str, Any]] = None,
        format_conversion: Optional[Dict[str, Any]] = None,
        filename_template: Optional[str] = None,
        output_directory: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Create a list of batch operations
        
        Args:
            metadata_updates: Dictionary of metadata fields to update
            cover_action: Cover art action (add/remove)
            format_conversion: Format conversion settings
            filename_template: Template for renaming files
            output_directory: Output directory for processed files
        
        Returns:
            List of operation dictionaries
        """
        operations = []
        
        # Add metadata update operation
        if metadata_updates:
            operations.append({
                'type': 'update_metadata',
                'params': metadata_updates
            })
        
        # Add cover art operation
        if cover_action:
            if cover_action.get('action') == 'add':
                operations.append({
                    'type': 'add_cover',
                    'params': {
                        'cover_data': cover_action.get('cover_data'),
                        'mime_type': cover_action.get('mime_type', 'image/jpeg')
                    }
                })
            elif cover_action.get('action') == 'remove':
                operations.append({
                    'type': 'remove_cover',
                    'params': {}
                })
        
        # Add format conversion operation
        if format_conversion:
            operations.append({
                'type': 'convert_format',
                'params': {
                    'format': format_conversion.get('format'),
                    'bitrate': format_conversion.get('bitrate'),
                    'output_dir': output_directory or format_conversion.get('output_dir')
                }
            })
        
        # Add file renaming operation
        if filename_template:
            operations.append({
                'type': 'rename_file',
                'params': {
                    'template': filename_template,
                    'output_dir': output_directory
                }
            })
        
        return operations
    
    def validate_files(self, file_paths: List[str]) -> Dict[str, List[str]]:
        """
        Validate a list of files
        
        Returns:
            Dictionary with 'valid' and 'invalid' file lists
        """
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                invalid_files.append(f"{file_path} (file not found)")
                continue
            
            extension = os.path.splitext(file_path)[1].lower()
            if extension not in self.audio_processor.supported_formats:
                invalid_files.append(f"{file_path} (unsupported format)")
                continue
            
            valid_files.append(file_path)
        
        return {
            'valid': valid_files,
            'invalid': invalid_files
        }
    
    def estimate_processing_time(
        self,
        file_count: int,
        operations_count: int,
        average_file_size_mb: float = 5.0
    ) -> Dict[str, float]:
        """
        Estimate processing time for batch operations
        
        Returns:
            Dictionary with time estimates in seconds
        """
        # Base processing time per file (seconds)
        base_time_per_file = 2.0
        
        # Additional time per operation
        operation_time = {
            'update_metadata': 0.5,
            'add_cover': 1.0,
            'remove_cover': 0.3,
            'convert_format': average_file_size_mb * 0.5,  # Depends on file size
            'rename_file': 0.2
        }
        
        # Calculate total time
        total_time = file_count * base_time_per_file
        total_time += file_count * operations_count * 1.0  # Average operation time
        
        # Account for parallel processing
        parallel_time = total_time / min(self.max_workers, file_count)
        
        return {
            'sequential_time': total_time,
            'parallel_time': parallel_time,
            'estimated_time': parallel_time * 1.2  # Add 20% buffer
        }