import os, sys

sys.path.append(os.path.abspath(os.path.join(__file__, "../../..")))
from lib.s3.rgw import Config
from lib.s3.rgw import RGWMultpart
import lib.s3.rgw as rgw_lib
import utils.log as log
import sys
from utils.test_desc import AddTestInfo
import argparse
import yaml


def test_exec(config):
    test_info = AddTestInfo('multipart Upload with cancel and download')

    try:

        # test case starts

        test_info.started_info()

        all_user_details = rgw_lib.create_users(config.user_count)

        log.info('multipart upload enabled')

        for each_user in all_user_details:
            each_user['port'] = config.port

            rgw = RGWMultpart(each_user)

            rgw.break_upload_at_part_no = config.break_at_part_no
            rgw.upload(config)

            log.info('starting at part no: %s' % config.break_at_part_no)
            log.info('--------------------------------------------------')

            rgw.break_upload_at_part_no = 0
            rgw.upload(config)
            rgw.download()

        test_info.success_status('test completed')

        sys.exit(0)

    except AssertionError, e:
        log.error(e)
        test_info.failed_status('test failed: %s' % e)
        sys.exit(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='RGW Automation')

    parser.add_argument('-c', dest="config", default='yamls/config.yaml',
                        help='RGW Test yaml configuration')

    parser.add_argument('-p', dest="port", default='8080',
                        help='port number where RGW is running')

    args = parser.parse_args()

    yaml_file = args.config

    with open(yaml_file, 'r') as f:
        doc = yaml.load(f)

    config = Config()

    config.user_count = doc['config']['user_count']
    config.bucket_count = doc['config']['bucket_count']
    config.objects_size_range = {'min': doc['config']['objects_size_range']['min'],
                                 'max': doc['config']['objects_size_range']['max']}

    config.break_at_part_no = doc['config']['break_at_part_no']

    config.port = args.port

    log.info('user_count:%s\n'
             'bucket_count: %s\n'
             'port: %s\n'
             'object_min_size: %s\n'
             'break at part number: %s\n'
             % (
             config.user_count, config.bucket_count, config.port, config.objects_size_range, config.break_at_part_no))

    test_exec(config)