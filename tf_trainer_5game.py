import tensorflow as tf
from tensorflow.contrib.session_bundle import exporter
from modules.bcolors.bcolors import bcolors
import sys

def combine_inputs(X):
    player = tf.reshape(tf.slice(X, [0, 0], [-1, 5]), [-1, 1, 1, 5])
    game = tf.reshape(tf.slice(X, [0, 5], [-1, 75]), [-1, 5, 15, 1])

    conv = tf.contrib.layers.convolution2d(game, 30,
        kernel_size=(1,15),
        stride=(1,15),
        activation_fn=tf.nn.relu,
        weights_initializer=tf.random_normal,
        biases_initializer=tf.random_normal,
        trainable=True)

    gamesfnn = tf.contrib.layers.stack(tf.reshape(conv, [-1, 1, 1, 150]), tf.contrib.layers.fully_connected, [100, 90, 50])

    playerfnn = tf.contrib.layers.fully_connected(
        player,
        50,
        biases_initializer=tf.random_normal
        )

    playerandgamesfnn = tf.contrib.layers.stack(
        tf.concat(3, [playerfnn, gamesfnn]),
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
    return loss, evaluation, predicted

def inputs():
    input_list = read_csv(300, [[0.0], [""], [0.0], [0.0], [0.0], [0.0], [0.0]] + [[0.0]] * 15*5)
    features = tf.transpose(tf.pack(input_list[2:]))
    cheat = tf.to_float(tf.equal(input_list[0], [1]))
    legit = tf.to_float(tf.equal(input_list[0], [0]))
    cheating = tf.transpose(tf.pack([legit, cheat]))
    return features, cheating

def train(total_loss):
    learning_rate = 0.00001
    #return tf.train.GradientDescentOptimizer(learning_rate).minimize(total_loss)
    return tf.train.AdamOptimizer(learning_rate).minimize(total_loss)

def evaluate(X, Y):
    with tf.name_scope("evaluate"):
        predicted = tf.cast(inference(X) > 0.5, tf.float32)
        loss = tf.reduce_mean(tf.cast(tf.equal(predicted, Y), tf.float32))
        return loss
    
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

graph = tf.Graph()
with graph.as_default():
    with tf.Session(graph=graph) as sess:
        X, Y = inputs()
        ## initliase graph for running
        with tf.name_scope("global_ops"):
            writer = tf.train.SummaryWriter('./tf_graph', graph)
            total_loss, evaluation, comp = loss(X, Y)
            train_op = train(total_loss)
            #test = combine_inputs(X)
            
            merged_summaries = tf.merge_all_summaries()
            training_steps = 1000
            saver = tf.train.Saver()
            tf.initialize_all_variables().run()
            coord = tf.train.Coordinator()
            threads = tf.train.start_queue_runners(sess=sess, coord=coord)

        #print "comp", sess.run([Y])
        for step in range(training_steps):
            sess.run([train_op])
            if step % 100 == 0:
                loss, eva, compar = sess.run([total_loss, evaluation, comp])
                #writer.add_summary(summary, global_step=step)
                for i in compar:
                    print i
                print "loss: ", loss
                print "eval: ", eva
                print " "
            
            if step%1000 == 0:
                saver.save(sess, 'my-model', global_step=step)
        coord.request_stop()
        coord.join(threads)
        writer.flush()
        writer.close()
        saver.save(sess, 'my-model', global_step=training_steps)

        export_path = sys.argv[-1]
        print 'Exporting trained model to', export_path
        saver = tf.train.Saver(sharded=True)
        model_exporter = tf.contrib.session_bundle.exporter.Exporter(saver)
        model_exporter.init(
            sess.graph.as_graph_def(),
            named_graph_signatures={
                'inputs': exporter.generic_signature({'images': X}),
                'outputs': exporter.generic_signature({'scores': comp})})
        model_exporter.export(export_path, tf.constant(FLAGS.export_version), sess)

        sess.close()