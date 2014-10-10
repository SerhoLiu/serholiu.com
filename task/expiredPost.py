#!/usr/bin/env python
import pika
import os
import shutil

QUEUE_NAME = 'ArticalChange'
CACHE_DIR = '/opt/data/product/blog/cache'
CACHE_BLOG_DIR = '/opt/data/product/blog/cache/blog'
CACHE_TAG_DIR = '/opt/data/product/blog/cache/tag'

def msg_recv_callback(ch, method, properties, body):
    print " [x] Received %r" % (body,)
    cache_file = CACHE_DIR + "/" + body + ".html"
    print cache_file

    if (os.path.exists(cache_file)):
        try:
            os.remove(cache_file)
            print 'remove %s success' % cache_file
        except OSError, e:
            #Same exception handling
            print '[Error]Remove file error.'

    try:
        print 'begin to remove dir[blog] and dir[tag]'
        shutil.rmtree(CACHE_BLOG_DIR, True)
        shutil.rmtree(CACHE_TAG_DIR, True)
    except shutil.Error, e:
        print '[Error] remove %s fail.' % CACHE_BLOG_DIR
        print '[Error] remove %s fail.' % CACHE_TAG_DIR


def receive_msg_loop():
    connection = pika.BlockingConnection(pika.ConnectionParameters(
            host='localhost'))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)

    print ' [*] Waiting for messages. To exit press CTRL+C'

    channel.basic_consume(msg_recv_callback,
                          queue=QUEUE_NAME,
                          no_ack=True)
    channel.start_consuming()

if __name__ == '__main__':
    receive_msg_loop()
