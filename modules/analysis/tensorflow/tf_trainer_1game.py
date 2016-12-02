import tensorflow as tf
import os

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
    entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(comb, Y))
    predicted = tf.round(tf.nn.softmax(comb))
    evaluation = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), tf.float32))
    return entropy, evaluation, tf.concat(1, [comb, predicted, Y])

def inputs():
    input_list = read_csv(800, [[0.0], [""], [0.0], [0.0], [0.0], [0.0], [0.0]] + [[0.0]] * 15)
    features = tf.transpose(tf.pack(input_list[2:]))
    cheat = tf.to_float(tf.equal(input_list[0], [1]))
    legit = tf.to_float(tf.equal(input_list[0], [0]))
    cheating = tf.transpose(tf.pack([legit, cheat]))
    return features, cheating

def train(total_loss):
    learning_rate = 0.001
    return tf.train.AdamOptimizer(learning_rate).minimize(total_loss)

def evaluate(X, Y):
    with tf.name_scope("evaluate"):
        predicted = tf.cast(inference(X) > 0.5, tf.float32)
        return tf.reduce_mean(tf.cast(tf.equal(predicted, Y), tf.float32))
    
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
    graph = tf.Graph()
    with graph.as_default():
        with tf.Session(graph=graph) as sess:
            X, Y = inputs()
            ## initliase graph for running
            with tf.name_scope("global_ops"):
                total_loss, evaluation, comp = loss(X, Y)
                train_op = train(total_loss)
                saver = tf.train.Saver()
                tf.global_variables_initializer().run()
                coord = tf.train.Coordinator()
                threads = tf.train.start_queue_runners(sess=sess, coord=coord)

            initial_step = 0

            ckpt = tf.train.get_checkpoint_state('./models')
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)
                initial_step = int(ckpt.model_checkpoint_path.rsplit('-', 1)[1])
                
            if initial_step >= 10000:
                training_steps = initial_step + 1000
            else: 
                training_steps = 10000

            for step in range(initial_step, training_steps):
                sess.run([train_op])
                if step % 1000 == 0:
                    tloss, eva, compar = sess.run([total_loss, evaluation, comp])
                    p, n, tp, tn, fp, fn, ind = 1, 1, 0, 0, 0, 0, 0
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
                    print "loss: ", tloss
                    print "eval: ", eva
                    print " "
                    saver.save(sess, './models/model', global_step=step)

            coord.request_stop()
            coord.join(threads)
            saver.save(sess, './models/model', global_step=training_steps)
            saver = tf.train.Saver(sharded=True)
            sess.close()

def apply_net(batch):
    graph = tf.Graph()
    with graph.as_default():
        with tf.Session(graph=graph) as sess:
            a = tf.placeholder(tf.float32, shape=[None, 20])
            infer = inference(a)
            feed_dict = {a: batch}
            ## initliase graph for running
            with tf.name_scope("global_ops"):
                saver = tf.train.Saver()
                tf.global_variables_initializer().run()
                coord = tf.train.Coordinator()
                threads = tf.train.start_queue_runners(sess=sess, coord=coord)

            ckpt = tf.train.get_checkpoint_state('models')
            if ckpt and ckpt.model_checkpoint_path:
                saver.restore(sess, ckpt.model_checkpoint_path)

            result = sess.run([infer], feed_dict=feed_dict)
            coord.request_stop()
            coord.join(threads)
            sess.close()
            return result

if __name__ == "__main__":
    learn()
