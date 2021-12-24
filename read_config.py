import configparser


def read_conf(path):
    config = configparser.ConfigParser()
    config.read(path, encoding='UTF-8')

    train_file = config['训练样本路径']['train_path']
    epoch = config.getfloat('训练参数', 'epoch')
    IR = config.getfloat('训练参数', 'IR')
    batch_size = config.getfloat('训练参数', 'batch_size')

    return train_file, epoch, IR, batch_size


if __name__ == '__main__':
    train_path = 'config.config'
    read_conf(train_path)
