from data.t2m_dataset import Text2MotionDatasetEval, collate_fn # TODO
from utils.word_vectorizer import WordVectorizer
import numpy as np
from os.path import join as pjoin
from torch.utils.data import DataLoader
from utils.get_opt import get_opt

def get_dataset_motion_loader(opt_path, batch_size, fname, device,txt_name=''):
    opt = get_opt(opt_path, device)
    opt.meta_dir = pjoin(opt.checkpoints_dir, opt.vq_name, 'meta')
    mean = np.load(pjoin(opt.meta_dir, 'mean.npy'))
    std = np.load(pjoin(opt.meta_dir, 'std.npy'))

    w_vectorizer = WordVectorizer('./glove', 'our_vab')
    split_file = pjoin(opt.data_root, '%s.txt'%fname)
    dataset = Text2MotionDatasetEval(opt, mean, std, split_file, w_vectorizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, num_workers=4, drop_last=True,
                            collate_fn=collate_fn, shuffle=True)
    
    print('Ground Truth Dataset Loading Completed!!!')
    return dataloader, dataset