import tensorflow as tf
from tensorflow import keras
from keras import layers
import numpy as np

model = keras.models.load_model("./solver.keras")

characters = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
max_length = 6

# Mapping characters to integers
char_to_num = layers.StringLookup(vocabulary=list(characters), mask_token=None)

# Mapping integers back to original characters
num_to_char = layers.StringLookup(
    vocabulary=char_to_num.get_vocabulary(), mask_token=None, invert=True
)

def decode_batch_predictions(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
        :, :max_length
    ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = tf.strings.reduce_join(num_to_char(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text

img_height = 35
img_width = 140

def encode_single_sample(img):
    # 2. Decode and convert to grayscale
    img = tf.io.decode_png(img, channels=1)
    #img = tf.io.decode_jpeg(img, channels=1)
    # 3. Convert to float32 in [0, 1] range
    img = tf.image.convert_image_dtype(img, tf.float32)
    # 4. Resize to the desired size
    img = tf.image.resize(img, [img_height, img_width])
    # 5. Transpose the image because we want the time
    # dimension to correspond to the width of the image.
    img = tf.transpose(img, perm=[1, 0, 2])
    return img

# A utility function to decode the output of the network
def decode_batch_predictions(pred):
    input_len = np.ones(pred.shape[0]) * pred.shape[1]
    # Use greedy search. For complex tasks, you can use beam search
    results = keras.backend.ctc_decode(pred, input_length=input_len, greedy=True)[0][0][
        :, :max_length
    ]
    # Iterate over the results and get back the text
    output_text = []
    for res in results:
        res = tf.strings.reduce_join(num_to_char(res)).numpy().decode("utf-8")
        output_text.append(res)
    return output_text


def solve(image):
    preds = model.predict(np.array([image]))
    results = decode_batch_predictions(preds)
    return results[0]

def solvePngFile(img_path):
    tfimage = tf.io.read_file(img_path)
    sample = encode_single_sample(tfimage)
    result = solve(sample)
    return result

def solvePngString(data):
    tfimage = tf.convert_to_tensor(data, dtype=tf.string)
    sample = encode_single_sample(tfimage)
    result = solve(sample)
    return result
"""
solvePngFile("./captcha_images/000172.png")
with open("./captcha_images/000172.png", 'rb') as file:
    data = file.read()
    solvePngString(data)

    """