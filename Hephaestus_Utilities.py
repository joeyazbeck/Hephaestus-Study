import zipfile
import matplotlib.pyplot as plt
import io
import json

#Code that contains various utilities related to the Hephaestus dataset.
#Funtions include retrieving images, labels, images given labels, and labels given images.

def ReturnEarthquakeImage():
    earthquake_annotations=[]
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref:
        annotation_file_names_list=zip_ref.namelist()
        for name in annotation_file_names_list[1:]:
            with zip_ref.open(name) as file:
                annotation=json.load(file)
                if (annotation['is_crowd'] == 0 and
                    'Earthquake' in annotation['label'] and
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
                    earthquake_annotations.append(name)
                    
    LookUpAssociatedImage(earthquake_annotations[0], plot=True)
    ReturnAnnotation(earthquake_annotations[0], print_caption=True)
    
    return earthquake_annotations

def ReturnImage(image_file_name):
    '''
    Description
    ----------
    Function that returns and displays an InSAR image given the image file name from the
    zipped image folder downloaded from the Hephaestus paper.
    
    Parameters
    ----------
    image_file_name : string (98)
        Image file name inside the images zipped folder.
        (example: 'LiCSAR-web-tools/133D_09451_141313/interferograms/20210227_20210416/20210227_20210416.geo.diff.png')

    Returns
    -------
    image : array of float32 (852,833,4)
        Array containing the RGB channels as well as the segmentation mask.
    '''
    
    images_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//Hephaestus_Raw.zip'
    
    with zipfile.ZipFile(images_zipped_folder_path,'r') as zip_ref:
        with zip_ref.open(image_file_name) as file:
            image_bytes=io.BytesIO(file.read())
    
    image=plt.imread(image_bytes)
    plt.imshow(image)
    #NEED TO SET CUSTOM COLORBAR I THINK
    plt.colorbar()
    plt.show()
    
    return image

def LookUpAssociatedImage(annotation_file_name, plot):
    '''
    Description
    ----------
    Function that returns and displays the image associated with the given annotation.

    Parameters
    ----------
    annotation_file_name : string (21)
        annotation file name from the annotation zipped folder.
        (example: 'annotations/9964.json')
        
    plot : boolean
        set to True to plot.

    Returns
    -------
    image : array of float32 (852,833,4)
        Array containing the RGB channels as well as the segmentation mask.
    '''
    
    annotations_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//annotations_hephaestus.zip'
    images_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//Hephaestus_Raw.zip'
    
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref_1:
        with zip_ref_1.open(annotation_file_name) as file_1:
            annotation=json.load(file_1)
            #Save information needed to access the associated image
            frameID=annotation['frameID']
            primary_date=annotation['primary_date']
            secondary_date=annotation['secondary_date']
            combined_date=primary_date+'_'+secondary_date
            #Open associated image file
            with zipfile.ZipFile(images_zipped_folder_path,'r') as zip_ref_2:
                with zip_ref_2.open('LiCSAR-web-tools/'+frameID+'/interferograms/'+combined_date+'/'+combined_date+'.geo.diff.png') as file_2:
                    image_bytes=io.BytesIO(file_2.read())
    image=plt.imread(image_bytes)
    
    if plot == True:
        plt.imshow(image)
        #NEED TO SET CUSTOM COLORBAR I THINK
        # plt.colorbar()
        plt.savefig('insar_image.pdf')
        plt.show()
    
    return image

def ReturnAnnotation(annotation_file_name, print_caption):
    '''
    Description
    ----------
    Function that returns an annotation given the annotation file name from the zipped
    annotation folder downloaded from the Hephaestus paper. It also prints the caption.
    
    Parameters
    ----------
    annotation_file_name : string (21)
        annotation file name from the annotation zipped folder.
        (example: 'annotations/9964.json')
        
    print_caption: boolean
        set to True to print the caption

    Returns
    -------
    annotation : dictionary (20)
        A python dictionary containing 20 different labels describing the image.
    '''
    
    annotations_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//annotations_hephaestus.zip'
    
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref:
        with zip_ref.open(annotation_file_name) as file:
            annotation=json.load(file)
            
    if print_caption == True:
        print(annotation['caption'])
    
    return annotation

def LookUpAssociatedAnnotation(image_file_name):
    '''
    Description
    ----------
    Function that returns an annotation associated with the given image. It also prints
    the caption.
    

    Parameters
    ----------
    image_file_name : string (98)
        Image file name inside the images zipped folder.
        (example: 'LiCSAR-web-tools/133D_09451_141313/interferograms/20210227_20210416/20210227_20210416.geo.diff.png')

    Returns
    -------
    annotation : dictionary (20)
        A python dictionary containing 20 different labels describing the image.
    '''
    
    annotations_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//annotations_hephaestus.zip'
    
    
    frameID=image_file_name[17:34]
    primary_date=image_file_name[50:58]
    secondary_date=image_file_name[59:67]
    
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref:
        annotation_file_names_list=zip_ref.namelist()
        for annotation_file_name in annotation_file_names_list[1:]:
            with zip_ref.open(annotation_file_name) as file:
                annotation=json.load(file)
                if (annotation['primary_date'] == primary_date and
                    annotation['secondary_date'] == secondary_date and
                    annotation['frameID'] == frameID):
                    break
                
    print(annotation['caption'])
    
    return annotation



if __name__ == "__main__":
    
    annotations_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//annotations_hephaestus.zip'
    images_zipped_folder_path='D://InSAR Stuff//Hephaestus Data//Hephaestus_Raw.zip'
    
    with zipfile.ZipFile(annotations_zipped_folder_path,'r') as zip_ref:
        annotation_file_names_list=zip_ref.namelist()
    with zipfile.ZipFile(images_zipped_folder_path,'r') as zip_ref:
        image_file_names_list=zip_ref.namelist()
    
    del zip_ref
    
    ReturnEarthquakeImage()
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    