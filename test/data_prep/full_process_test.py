"""" Test Full Data Processing Pipeline """
import tensorflow as tf

from data_processing.data_inventory import DatasetInventoryMaster
from data_processing.data_writer import DatasetWriter
from data_processing.tfr_encoder_decoder import SingleObsTFRecordEncoderDecoder
from data_processing.data_reader import DatasetReader
from pre_processing.image_transformations import (
        preprocess_image,
        resize_jpeg)


path = './test/test_images'
source_type = 'image_dir'
params = {'path': path}
dinv = DatasetInventoryMaster()
dinv.create_from_source(source_type, params)

dinv._calc_label_stats()
dinv.log_stats()

#dinv.export_to_json('./test/dummy.json')

splitted = dinv.split_inventory_by_random_splits_with_balanced_sample(
        split_label_min='class',
        split_names=['train', 'val', 'test'],
        split_percent=[0.6, 0.2, 0.2])


tfr = {k: v.create_tfrecord_dict() for k, v in splitted.items()}


tfr_encoder_decoder = SingleObsTFRecordEncoderDecoder()

writer = DatasetWriter(tfr_encoder_decoder.encode_record)


path = './test/tfr_test.tfrecord'
writer.encode_to_tfr(tfr['test'], path)

reader = DatasetReader(tfr_encoder_decoder.decode_record)

image_processing = {'output_height': 224,
      'output_width': 224,
      'resize_side_min': 224,
      'resize_side_max': 246,
      'color_manipulations': True}

batch_data = reader.get_iterator(tfr_files=path, batch_size=3,
                    is_train=False,
                    n_repeats=1,
                    output_labels = ['label/0/class'],
                    buffer_size=10,
                    num_parallel_calls=1,
                    image_pre_processing_fun=preprocess_image,
                    image_pre_processing_args={**image_processing,
                                   'is_training': False})


with tf.Session() as sess:
    data = sess.run(batch_data)




# Create Dataset
data['images']
data['id']
data['label/0/class']


import os
import random
import csv

output_file = './test/test_files/Cats_dogs.csv'

cats_files = os.listdir('./test/test_images/Cats')
dogs_files = os.listdir('./test/test_images/Dogs')

with open(output_file, 'w', newline='') as csvfile:
    csvwriter = csv.writer(csvfile, delimiter=',')
    csvwriter.writerow(['id', 'image', 'species', 'standing', 'count'])

    for i, cat in enumerate(cats_files):
        random.seed(i)
        random_standing = random.randint(0,1)
        random.seed(i)
        random_count = random.randint(1,15)
        record = [cat, './test/test_images/Cats/' + cat, 'cat', str(random_standing), str(random_count)]
        csvwriter.writerow(record)


    for i, dog in enumerate(dogs_files):
        random.seed(i)
        random_standing = random.randint(0,1)
        random.seed(i)
        random_count = random.randint(1,15)
        record = [dog, './test/test_images/Dogs/' + dog, 'dog', str(random_standing), str(random_count)]
        csvwriter.writerow(record)






path = './test/test_files/Cats_dogs.csv'
source_type = 'csv'
params = {'path': path,
          'image_path_col_list': 'image',
          'capture_id_col': 'id',
          'attributes_col_list': ['species', 'count', 'standing']}

dinv = DatasetInventoryMaster()
dinv.create_from_source(source_type, params)

dinv._calc_label_stats()
dinv.log_stats()

#dinv.export_to_json('./test/dummy.json')

splitted = dinv.split_inventory_by_random_splits_with_balanced_sample(
        split_label_min='species',
        split_names=['train', 'val', 'test'],
        split_percent=[0.6, 0.2, 0.2])


tfr = {k: v.create_tfrecord_dict() for k, v in splitted.items()}


tfr_encoder_decoder = SingleObsTFRecordEncoderDecoder()

writer = DatasetWriter(tfr_encoder_decoder.encode_record)


path = './test/tfr_train_cat_dog.tfrecord'
writer.encode_to_tfr(tfr['train'], path)

reader = DatasetReader(tfr_encoder_decoder.decode_record)

image_processing = {'output_height': 224,
      'output_width': 224,
      'resize_side_min': 224,
      'resize_side_max': 246,
      'color_manipulations': True}

batch_data = reader.get_iterator(tfr_files=path, batch_size=3,
                    is_train=False,
                    n_repeats=1,
                    output_labels = ['label/0/species', 'label/0/count'],
                    buffer_size=10,
                    num_parallel_calls=1,
                    image_pre_processing_fun=preprocess_image,
                    image_pre_processing_args={**image_processing,
                                   'is_training': False})


with tf.Session() as sess:
    data = sess.run(batch_data)
data['id']







