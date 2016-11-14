import tensorflow as tf

def combine_inputs(X):
    with tf.name_scope("main graph"):
        conv = tf.contrib.layers.convolution2d(X, 1,
            kernel_size=(1,1),
            stride=(1,1),
            trainable=True)
        return conv

def inference(X):
    return tf.sigmoid(combine_inputs(X))

def loss(X, Y):
    return tf.reduce_mean(tf.nn.sigmoid_cross_entropy_with_logits(combine_inputs(X), Y))

def inputs():
    #cheating,name,titled,closed_reports,blocker_to_followers,cheaters_to_legits,games_played,
    #mb1,mb2,mb3,mb4,mb5,hb1,hb2,hb3,hb4,hb5,h1,h2,h3,h4,h5,m1,m2,m3,m4,m5,
    #s1,s2,s3,s4,s5,r01,r02,r03,r04,r05,r11,r12,r13,r14,r15,r51,r52,r53,r54,r55,
    #r020p1,r020p2,r020p3,r020p4,r020p5,r01220p1,r01220p2,r01220p3,r01220p4,r01220p5,
    #cp201,cp202,cp203,cp204,cp205,cp101,cp102,cp103,cp104,cp105,cp1001,cp1002,cp1003,cp1004,cp1005,
    #cpar11,cpar12,cpar13,cpar14,cpar15,cpar21,cpar22,cpar23,cpar24,cpar25
    input_list = read_csv(200, [[0.0], [""], [0.0], [0.0], [0.0], [0.0], [0.0]] + [[0.0]] * 15*5)
    features = tf.transpose(tf.pack(input_list[2:]))
    cheating = tf.reshape(input_list[0], [200, 1])
    return features, cheating

def train(total_loss):
    learning_rate = 0.01
    return tf.train.GradientDescentOptimizer(learning_rate).minimize(total_loss)

def evaluate(sess, X, Y):
    predicted = tf.cast(inference(X) > 0.5, tf.float32)
    print sess.run(tf.reduce_mean(tf.cast(tf.equal(predicted, Y), tf.float32)))
    
def read_csv(batch_size, record_defaults):
    filename_queue = tf.train.string_input_producer(['test-data/player_data.csv'])
    reader = tf.TextLineReader(skip_header_lines=1)
    key, value = reader.read(filename_queue)
    decoded = tf.decode_csv(value, record_defaults=record_defaults)
    return tf.train.shuffle_batch(decoded,
        batch_size=batch_size,
        capacity=batch_size*50,
        num_threads=4,
        min_after_dequeue=batch_size*10)

#saver = tf.train.Saver()
config = tf.ConfigProto(inter_op_parallelism_threads=2)
with tf.Session(config=config) as sess:
    tf.initialize_all_variables().run()
    X, Y = inputs()
    coord = tf.train.Coordinator()
    output = tf.map_fn(lambda img: tf.reshape(img[5:][:], [5, 15, 1]), X)
    threads = tf.train.start_queue_runners(sess=sess, coord=coord)
    print sess.run([output])
    #print sess.run([tf.reshape(X[5:], [200, 5, 15, 1])])
    #print sess.run([combine_inputs(X)])
    """
    total_loss = loss(X, Y)
    train_op = train(total_loss)
    """

    """
    training_steps = 10000
    for step in range(training_steps):
        sess.run([train_op])
        if step % 100 == 0:
            print "loss: ", sess.run([total_loss])
        
        if step%1000 == 0:
            saver.save(sess, 'my-model', global_step=step)
    
    evaluate(sess, X, Y)
    
    saver.save(sess, 'my-model', global_step=training_steps)
    """
    coord.request_stop()
    coord.join(threads)
    sess.close()