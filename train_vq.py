import os
from os.path import join as pjoin

import torch
from torch.utils.data import DataLoader

from models.vq.model import RVQVAE
from models.vq.vq_trainer import RVQTokenizerTrainer
from options.vq_option import arg_parse
from data.t2m_dataset import MotionDataset
from utils import paramUtil
import numpy as np

from models.t2m_eval_wrapper import EvaluatorModelWrapper
from utils.get_opt import get_opt
from motion_loaders.dataset_motion_loader import get_dataset_motion_loader

from utils.motion_process import recover_from_ric
from utils.plot_script import plot_3d_motion
from utils.fixseed import fixseed

os.environ["OMP_NUM_THREADS"] = "1"

def plot_t2m(data, save_dir):
    data = train_dataset.inv_transform(data)
    for i in range(len(data)):
        joint_data = data[i]
        joint = recover_from_ric(torch.from_numpy(joint_data).float(), opt.joints_num).numpy()
        if i<4:
            save_path = pjoin(save_dir, '%02d_gt.gif' % (i))
            plot_3d_motion(save_path, kinematic_chain, joint, title="None", fps=fps, radius=radius)
            np.save(pjoin(save_dir, '%02d_gt.npy' % (i)), joint)
        else:
            save_path = pjoin(save_dir, '%02d_pred.gif' % (i-4))
            plot_3d_motion(save_path, kinematic_chain, joint, title="None", fps=fps, radius=radius)

if __name__ == "__main__":
    opt = arg_parse(True)
    fixseed(opt.seed)

    opt.device = torch.device("cpu" if opt.gpu_id == -1 else "cuda:" + str(opt.gpu_id))
    print(f"Using Device: {opt.device}")

    opt.save_root = pjoin(opt.checkpoints_dir, opt.name)
    opt.model_dir = pjoin(opt.save_root, 'model')
    opt.meta_dir = pjoin(opt.save_root, 'meta')
    opt.eval_dir = pjoin(opt.save_root, 'animation')
    opt.log_dir = pjoin('./log/vq/', opt.name)

    os.makedirs(opt.model_dir, exist_ok=True)
    os.makedirs(opt.meta_dir, exist_ok=True)
    os.makedirs(opt.eval_dir, exist_ok=True)
    os.makedirs(opt.log_dir, exist_ok=True)

    opt.data_root = f'./AniMo4D'
    opt.motion_dir = pjoin(opt.data_root, f'new_joint_vecs')
    opt.text_dir = pjoin(opt.data_root, f'texts')
    opt.joints_num = 30
    dim_pose = 359
    fps = 20
    radius = 2
    opt.max_motion_length = 300
    kinematic_chain = paramUtil.animo_kinematic_chain
    dataset_opt_path = f'./{opt.checkpoints_dir}/{opt.name}/opt.txt'
    wrapper_opt = get_opt(dataset_opt_path, torch.device('cuda'))   # eval
    eval_wrapper = EvaluatorModelWrapper(wrapper_opt)

    mean = np.load(pjoin(opt.data_root, 'Mean.npy'))
    std = np.load(pjoin(opt.data_root, 'Std.npy'))

    train_split_file = pjoin(opt.data_root, 'train.txt')
    val_split_file = pjoin(opt.data_root, 'val.txt')


    net = RVQVAE(opt,
                dim_pose,
                opt.nb_code,
                opt.code_dim,
                opt.code_dim,
                opt.down_t,
                opt.stride_t,
                opt.width,
                opt.depth,
                opt.dilation_growth_rate,
                opt.vq_act,
                opt.vq_norm)

    pc_vq = sum(param.numel() for param in net.parameters())
    print('Total parameters of all models: {}M'.format(pc_vq/1000_000))
    trainer = RVQTokenizerTrainer(opt, vq_model=net)
    train_dataset = MotionDataset(opt, mean, std, train_split_file)
    val_dataset = MotionDataset(opt, mean, std, val_split_file)
    print(f"Train Dataset Size: {len(train_dataset)}")
    print(f"Val Dataset Size: {len(val_dataset)}")
    train_loader = DataLoader(train_dataset, batch_size=opt.batch_size, drop_last=True, num_workers=4,
                              shuffle=True, pin_memory=True)
    val_loader = DataLoader(val_dataset, batch_size=opt.batch_size, drop_last=True, num_workers=4,
                            shuffle=True, pin_memory=True)
    eval_val_loader, _ = get_dataset_motion_loader(dataset_opt_path, 32, 'val', device=opt.device)
    trainer.train(train_loader, val_loader, eval_val_loader, eval_wrapper, plot_t2m)
