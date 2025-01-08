import numpy as np
import matplotlib.pyplot as plt
from tqdm import tqdm
import io
import json
import zipfile
import pickle
import datetime
from Hephaestus_Utilities import ReturnImage, ReturnAnnotation, LookUpAssociatedAnnotation, LookUpAssociatedImage
import random

#NEEDS UPDATING. PROBABLY JUST COPY PASTE FROM THE GIT PREPROCESSING SCRIPT.

#Code to retrieve images and labels from Hephaestus dataset after downloading it from Github
#while leaving the images and labels compressed (i.e. no extraction).
#The resulting dataset is saved as a pkl to be opened for machine learning purposes.


if __name__ == '__main__':
    
    
    ########################################################################################
    
    #Always track code running time
    start=datetime.datetime.now()
    
    ########################################################################################
    
    #DEFINING GLOBAL VARIABLES
    
    #Define zipped folder paths for the annotations and images
    annotations_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//annotations_hephaestus.zip'
    images_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//Hephaestus_Raw.zip'
    
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref:
        annotation_file_names_list=zip_ref.namelist()
    with zipfile.ZipFile(images_zipped_folder_path,'r') as zip_ref:
        image_file_names_list=zip_ref.namelist()
    
    del zip_ref
    
    ########################################################################################
    
    #10076.json has no deformation
    #1125.json has deformation
    
    # #ACCESSING IMAGES (2 METHODS)
    
    # #DIRECT METHOD
    # image_file_name='LiCSAR-web-tools/133D_09451_141313/interferograms/20210227_20210416/20210227_20210416.geo.diff.png'
    # image=ReturnImage(image_file_name)
    
    # #INDIRECT METHOD USING SPECIFIED ANNOTATION
    # annotation_file_name='annotations/6158.json'
    # image=LookUpAssociatedImage(annotation_file_name, plot=True)
    
    ########################################################################################
    
    # #ACCESSING ANNOTATIONS (2 METHODS)
    
    # #DIRECT METHOD
    # annotation_file_name='annotations/6158.json'
    # annotation=ReturnAnnotation(annotation_file_name, print_caption=True)
    
    # #INDIRECT METHOD USING SPECIFIED IMAGE
    # image_file_name='LiCSAR-web-tools/133D_09451_141313/interferograms/20210227_20210416/20210227_20210416.geo.diff.png'
    # annotation=LookUpAssociatedAnnotation(image_file_name)
    
    ########################################################################################
    
    #EXPLORING PARAMETER RESTRICTION
    
    #I need to be systematic about this. Follow the paper's order.
    # 1) 'confidence': The max confidence is 0.8 AND if I set the minimum confidence to 0.8,
    #I am left with 19,454 images out of the original 19,920 images. (i.e. 98% of dataset)
    # 2) 'label': Set to not equal to 'non_deformation' so basically only include the
    #deforming and earthquake images.
    # 3) 'no_info': There are 220 images with no info. Look into this as a non-deforming
    #restriction.
    # 4) 'corrupted': 19607/19919 images not corrupted
    # 5) 'processing_error': I want type 0. 19423/19919 images with no processing error
    # 6) 'glacier_fringes': == 0
    # 7) 'orbital_fringes': == 0
    # 8) 'atmospheric_fringes': I cannot set this to 0 because it'll result in too little
    #images left over. Maybe just do <=2 and leave out type 3 which is a combination of 1
    #and 2 which could be chaotic for the AI to discern.
    # 9) 'low_coherence': set to 0
    # 10) 'no_info': set to 0
    # 11) 'image_artifacts': set to 0
    # 12) 'is_crowd': set to 0. Could be argued that I can set it to either 1 or 0 in
    #order to make the model more resilient perhaps. For now, I don't want to confuse
    #the model.
    # 13) 'activity_type': I don't want 'Unidentified'. Be careful! if you were to set
    #the parameter 'is_crowd' to 0 or 1, then 'activity_type' will be a list with 2 or more
    #elements inside it! So be careful in the 'if' condition.
    # Important note regarding why 'label' is a list. The reason is because there can be
    #'deformation' as well as 'earthquake' at the same time, so in that case, 'label' will
    #have 2 elements, 'is_crowd' will be 1, 'activity_type' will have 2 elements (example:
    #Mogi, Earthquake), and 'intensity_level' will have 2 elements as well. However,
    #in the case where there are 2 'deformation', 'label' will be a list of size 1 just
    #indicating 'deformation', 'is_crowd' will be 1, 'activity_type' will be 2 or more, and
    #'intensity_level' will be 2 or more.
    
    #I CAN OPTIMIZE THIS EVEN FURTHER BY IMMEDIATELY SAVING AND APPENDING THE FILES
    #AS I SEARCH THROUGH THEM USING SOME KIND OF PROBABILITY OF CHOOSING IT BASED ON
    #THE TOTAL AMOUNT OF IMAGES NEEDED.
    
    
    clean_deforming_annotations=[]
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref:
        annotation_file_names_list=zip_ref.namelist()
        for name in annotation_file_names_list[1:]:
            with zip_ref.open(name) as file:
                annotation=json.load(file)
                if (annotation['is_crowd'] == 0 and
                    annotation['label'][0] != 'Non_Deformation' and
                    annotation['processing_error'] == 0 and
                    annotation['glacier_fringes'] == 0 and
                    annotation['orbital_fringes'] == 0 and
                    annotation['atmospheric_fringes'] <= 2 and
                    annotation['low_coherence'] == 0 and
                    annotation['no_info'] == 0 and
                    annotation['image_artifacts'] == 0 and
                    annotation['corrupted'] == 0 and
                    annotation['confidence'] >= 0.8 and
                    annotation['activity_type'][0] != 'Unidentified'):
                    clean_deforming_annotations.append(name)
                    
    print('Number of clean deforming images: ' + str(len(clean_deforming_annotations)))
    
    clean_nondeforming_annotations=[]
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref:
        annotation_file_names_list=zip_ref.namelist()
        for name in annotation_file_names_list[1:]:
            with zip_ref.open(name) as file:
                annotation=json.load(file)
                if (annotation['is_crowd'] == 0 and
                    annotation['label'][0] == 'Non_Deformation' and
                    annotation['processing_error'] == 0 and
                    annotation['glacier_fringes'] == 0 and
                    annotation['orbital_fringes'] == 0 and
                    annotation['atmospheric_fringes'] <= 2 and
                    annotation['low_coherence'] == 0 and
                    annotation['no_info'] == 0 and
                    annotation['image_artifacts'] == 0 and
                    annotation['corrupted'] == 0 and
                    annotation['confidence'] >= 0.8):
                    clean_nondeforming_annotations.append(name)
                    
    print('Number of clean non-deforming images: ' + str(len(clean_nondeforming_annotations)))
    
    ########################################################################################
    
    #SAVING DATASET
    
    #This is based on the fact that there are much more deforming images than
    #there are non-deforming images. So, I will take all the deforming images and will
    #randomly choose the rest from the non deforming images.
    #Can do a max of 1100? images
    total_images_wanted=800
    nondeforming_images_to_use=total_images_wanted-len(clean_deforming_annotations)
    nondeforming_annotations_chosen=random.sample(clean_nondeforming_annotations,nondeforming_images_to_use)
    
    
    images=[]
    annotations=[]
    
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref_1:
        with zipfile.ZipFile(images_zipped_folder_path,'r') as zip_ref_2:
            for file_name in tqdm(clean_deforming_annotations+nondeforming_annotations_chosen):
                with zip_ref_1.open(file_name) as file_1:
                    annotation=json.load(file_1)
                    #Append the entire annotation
                    annotations.append(annotation)
                    
                    #Extract info to find the associated image
                    frameID=annotation['frameID']
                    primary_date=annotation['primary_date']
                    secondary_date=annotation['secondary_date']
                    combined_date=primary_date+'_'+secondary_date
                    with zip_ref_2.open('LiCSAR-web-tools/'+frameID+'/interferograms/'+combined_date+'/'+combined_date+'.geo.diff.png') as file_2:
                        image_bytes=io.BytesIO(file_2.read())
                        image=plt.imread(image_bytes)
                        images.append(image)
    
    collection_of_variables={'images':images, 'annotations':annotations}
    
    # print('Saving Retrieved Images and Labels ...')
    # with open('D://InSAR Stuff//Hephaestus Data//images_and_annotations_dict.pkl','wb') as file:
    #     pickle.dump(collection_of_variables,file)
    # print('Saving completed successfully!')
    
    ########################################################################################
    
    #Always track code running time
    print('Total time code took: ' + str(datetime.datetime.now()-start))
    
    ########################################################################################
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    