import tensorflow as tf
import os
from modules.bcolors.bcolors import bcolors

graph = tf.Graph()

def combine_inputs(X):
    playerandgamesfnn = tf.contrib.layers.stack(X,
        tf.contrib.layers.fully_connected,
        [100, 40, 10, 10, 2]
        )

    return tf.reshape(playerandgamesfnn, [-1, 2])

def inference(X):
    return tf.nn.softmax(combine_inputs(X))

def loss(X, Y):
    comb = combine_inputs(X)
    loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(comb, Y))
    predicted = tf.round(tf.nn.softmax(comb))
    evaluation = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), tf.float32))
    return loss, evaluation, tf.concat(1, [comb, predicted, Y])

def inputs():
    input_list = read_csv(800, [[0.0], [""], [0.0], [0.0], [0.0], [0.0], [0.0]] + [[0.0]] * 15)
    features = tf.transpose(tf.pack(input_list[2:]))
    cheat = tf.to_float(tf.equal(input_list[0], [1]))
    legit = tf.to_float(tf.equal(input_list[0], [0]))
    cheating = tf.transpose(tf.pack([legit, cheat]))
    return features, cheating

def train(total_loss):
    learning_rate = 0.001
    #return tf.train.GradientDescentOptimizer(learning_rate).minimize(total_loss)
    return tf.train.AdamOptimizer(learning_rate).minimize(total_loss)

def evaluate(X, Y):
    with tf.name_scope("evaluate"):
        predicted = tf.cast(inference(X) > 0.5, tf.float32)
        loss = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), tf.float32))
        return loss
    
def read_csv(batch_size, record_defaults):
    filename_queue = tf.train.string_input_producer(['test-data/player_single_game_data.csv'])
    reader = tf.TextLineReader(skip_header_lines=1)
    key, value = reader.read(filename_queue)
    decoded = tf.decode_csv(value, record_defaults=record_defaults)
    return tf.train.shuffle_batch(decoded,
        batch_size=batch_size,
        capacity=batch_size*50,
        num_threads=4,
        min_after_dequeue=batch_size*10)



def learn():
    global loss
    with graph.as_default():
        with tf.Session(graph=graph) as sess:
            X, Y = inputs()
            
            ## initliase graph for running
            with tf.name_scope("global_ops"):
                total_loss, evaluation, comp = loss(X, Y)
                train_op = train(total_loss)
                shape = tf.shape(X)
                training_steps = 100000
                saver = tf.train.Saver()
                tf.initialize_all_variables().run()
                coord = tf.train.Coordinator()
                threads = tf.train.start_queue_runners(sess=sess, coord=coord)

            initial_step = 0

            ckpt = tf.train.get_checkpoint_state(os.path.dirname(__file__))
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                initial_step = int(ckpt.model_checkpoint_path.rsplit('-', 1)[1])

            for step in range(initial_step, training_steps):
                sess.run([train_op])
                if step % 1000 == 0:
                    loss, eva, compar, shape = sess.run([total_loss, evaluation, comp, shape])
                    p, n, tp, tn, fp, fn, ind = 1, 1, 0, 0, 0, 0, 0
                    print shape
                    for g in compar:
                        if g[4] == 1:
                            # if player should be marked as legit
                            if g[2] == 1. and g[3] == 0.:
                                tn += 1
                                n += 1
                            elif g[2] == 0. and g[3] == 1.:
                                fp += 1
                                p += 1
                            else:
                                ind += 1
                        else:
                            # if player should be marked as cheating
                            if g[2] == 1. and g[3] == 0.:
                                fn += 1
                                n += 1
                            elif g[2] == 0. and g[3] == 1.:
                                tp += 1
                                p += 1
                            else:
                                ind += 1
                    print compar
                    print "Step: ", step
                    print "True P:   " + str(100*tp/p) + "% (" + str(tp) + ")"
                    print "True N:   " + str(100*tn/n) + "% (" + str(tn) + ")"
                    print "False P:  " + str(100*fp/p) + "% (" + str(fp) + ")"
                    print "False N:  " + str(100*fn/n) + "% (" + str(fn) + ")"
                    print "Indecise: " + str(100*ind/800) + "% (" + str(ind) + ")"
                    print "loss: ", loss
                    print "eval: ", eva
                    print " "
                
                if step%1000 == 0:
                    saver.save(sess, 'model', global_step=step)

            coord.request_stop()
            coord.join(threads)
            saver.save(sess, 'model', global_step=training_steps)
            saver = tf.train.Saver(sharded=True)
            sess.close()

def apply_net(batch):
    with graph.as_default():
        with tf.Session(graph=graph) as sess:
            a = tf.placeholder(tf.float32, shape=[None, 20])
            infer = inference(a)
            feed_dict = {a: batch}
            ## initliase graph for running
            with tf.name_scope("global_ops"):
                saver = tf.train.Saver()
                tf.initialize_all_variables().run()
                coord = tf.train.Coordinator()
                threads = tf.train.start_queue_runners(sess=sess, coord=coord)

            ckpt = tf.train.get_checkpoint_state(os.path.dirname(__file__))
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)

            result = sess.run([infer], feed_dict=feed_dict)
            coord.request_stop()
            coord.join(threads)
            sess.close()
            return result

app = apply_net(
    [[0,0,0,0.0,4,0,0,0,0,20,68,10,17,0,0,82,79,6,3,0],
    [0,0,0,0.0,4,0,0,0,0,20,62,20,17,0,0,79,72,6,11,0],
    [0,0,0,0.0,4,0,0,0,0,20,68,10,17,0,0,75,72,6,28,0],
    [0,0,0,0.0,4,0,0,0,0,20,55,24,17,0,0,72,72,6,12,0],
    [0,0,0,0.0,4,0,0,0,0,20,65,17,17,0,0,75,75,6,12,0],
    [0,0,0,0,10,1,1,0,1,17,60,24,12,0,0,88,80,0,24,8],
    [0,0,0,0,10,1,1,0,0,65,42,19,23,0,0,80,71,4,5,12],
    [0,0,0,0,10,1,0,0,0,13,43,26,17,0,0,73,65,4,5,69],
    [0,0,0,0,10,1,1,0,0,17,41,23,11,0,0,61,47,5,43,34],
    [0,0,0,0,10,1,1,0,1,22,59,13,18,0,0,77,68,4,8,32]]
    )



for x in app:
    for i in x:
        if i[0] > i[1]:
            print "legit"
        elif i[1] > i[0]:
            print "cheat"
        else:
            print "indecise"
#learn()