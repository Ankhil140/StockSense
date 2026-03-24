import tensorflow as tf
import tf2onnx
import os
import glob

def convert_h5_to_onnx(h5_path):
    onnx_path = h5_path.replace('.h5', '.onnx')
    print(f"Converting {h5_path} to {onnx_path}...")
    
    try:
        model = tf.keras.models.load_model(h5_path)
        
        # Save as SavedModel first (more robust for LSTM)
        tmp_path = h5_path.replace('.h5', '_saved')
        model.export(tmp_path) # Use .export for Keras 3
        
        # Run conversion via command line for better stability
        import subprocess
        cmd = [
            "python", "-m", "tf2onnx.convert",
            "--saved-model", tmp_path,
            "--output", onnx_path,
            "--opset", "13"
        ]
        subprocess.run(cmd, check=True)
        
        # Cleanup
        import shutil
        shutil.rmtree(tmp_path)
            
        print(f"Successfully converted {h5_path}")
    except Exception as e:
        print(f"Failed to convert {h5_path}: {e}")

if __name__ == "__main__":
    model_files = glob.glob("models/*.h5")
    if not model_files:
        print("No .h5 models found.")
    else:
        for f in model_files:
            convert_h5_to_onnx(f)
