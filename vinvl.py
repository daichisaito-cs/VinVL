from transformers.pytorch_transformers import BertConfig, BertTokenizer
from oscar.modeling.modeling_bert import BertForImageCaptioning
from oscar.wrappers import OscarTensorizer
import torch
from scene_graph_benchmark.wrappers import VinVLVisualBackbone

import numpy as np

ckpt = "vinvl-base-image-captioning" # if you downloaded from huggingface
# ckpt = "path/to/the/checkpoint"
device = "cuda" if torch.cuda.is_available() else "cpu"

# original code
config = BertConfig.from_pretrained(ckpt)
tokenizer = BertTokenizer.from_pretrained(ckpt)
model = BertForImageCaptioning.from_pretrained(ckpt, config=config).to(device)

# This takes care of the preprocessing
tensorizer = OscarTensorizer(tokenizer=tokenizer, device=device)

# numpy-arrays with shape (1, num_boxes, feat_size)
# feat_size is 2054 by default in VinVL
img_file = "/home/initial/workspace/smilab23/operationCheck/vins/data/d88cf5a6d670aeed.jpg"
detector = VinVLVisualBackbone()
dets = detector(img_file)
v_feats = np.concatenate((dets['features'],  dets['spatial_features']), axis=1)
visual_features = torch.from_numpy(v_feats).to(device).unsqueeze(0)

# labels are usually extracted by the features extractor
labels = [['boat', 'boat', 'boat', 'bottom', 'bush', 'coat', 'deck', 'deck', 'deck', 'dock', 'hair', 'jacket']]

inputs = tensorizer.encode(visual_features, labels=labels)
outputs = model(**inputs)

pred = tensorizer.decode(outputs)
print(pred)
# the output looks like this:
# pred = {0: [{'caption': 'a red and white boat traveling down a river next to a small boat.', 'conf': 0.7070220112800598]}
