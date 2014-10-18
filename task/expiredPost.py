#!/usr/bin/env python
import pika
import os
import shutil

QUEUE_NAME = 'PostChange'
CACHE_DIR = '/opt/data/product/blog/cache'
CACHE_BLOG_DIR = '/opt/data/product/blog/cache/blog'
CACHE_TAG_DIR = '/opt/data/product/blog/cache/tag'

def msg_recv_callback(ch, method, properties, body):
    print "[Info] Received %r" % (body,)
    cache_file = CACHE_DIR + "/" + body + ".html"

    if (os.path.exists(cache_file)):
        try:
            os.remove(cache_file)
        except OSError:
            #Same exception handling
            print '[Error] remove file error.'
        else:
            print '[Info] remove %s success' % cache_file

    try:
        shutil.rmtree(CACHE_BLOG_DIR, True)
        shutil.rmtree(CACHE_TAG_DIR, True)
    except shutil.Error:
        print '[Error] remove %s fail.' % CACHE_BLOG_DIR
        print '[Error] remove %s fail.' % CACHE_TAG_DIR
    else:
        print '[Info] begin to remove dir[blog] and dir[tag]'

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
