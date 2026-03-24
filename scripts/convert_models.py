import tensorflow as tf
import os
import glob

def convert_h5_to_tflite(h5_path):
    tflite_path = h5_path.replace('.h5', '.tflite')
    print(f"Converting {h5_path} to {tflite_path}...")
    
    try:
        model = tf.keras.models.load_model(h5_path)
        
        # LSTM models often need a fixed batch size for TFLite conversion
        # We'll re-define the model or just set the input shape explicitly if possible
        # Alternatively, use concrete functions
        
        run_model = tf.function(lambda x: model(x))
        # Batch size 1, window size 60, 1 feature
        concrete_func = run_model.get_concrete_function(
            tf.TensorSpec([1, 60, 1], model.inputs[0].dtype)
        )
        
        converter = tf.lite.TFLiteConverter.from_concrete_functions([concrete_func])
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        
        tflite_model = converter.convert()
        
        with open(tflite_path, 'wb') as f:
            f.write(tflite_model)
        print(f"Successfully converted {h5_path}")
    except Exception as e:
        print(f"Failed to convert {h5_path}: {e}")

if __name__ == "__main__":
    model_files = glob.glob("models/*.h5")
    if not model_files:
        print("No .h5 models found in models/ directory.")
    else:
        for model_file in model_files:
            convert_h5_to_tflite(model_file)
