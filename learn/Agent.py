import tensorflow as tf
import numpy as np
import tensorflow.contrib.slim as slim

import time

class Agent():
    # lr = Learning rate
    # s_size = sample size
    # a_size = action size
    def __init__(self, app, lr=0.07):
        self.app = app

        tf.reset_default_graph() #Clear the Tensorflow graph.

        s_size = 1 # Train using only one gamestate
        a_size = 3 # Can only move left, right or nowhere
        h_size = 8 # Hidden layer size

        # The state_in is a vector of all input values
        self.state_in= tf.placeholder(shape=[None, 1 + self.app.engine.window.width()],dtype=tf.float32)
        hidden = slim.fully_connected(self.state_in,h_size,biases_initializer=None,activation_fn=tf.nn.relu)
        self.output = slim.fully_connected(hidden,a_size,activation_fn=tf.nn.softmax,biases_initializer=None)
        self.chosen_action = tf.argmax(self.output,1)


        # The next six lines establish the training proceedure.
        # We feed the reward and chosen action into the network
        # to compute the loss, and use it to update the network.
        self.reward_holder = tf.placeholder(shape=[None],dtype=tf.float32)
        self.action_holder = tf.placeholder(shape=[None],dtype=tf.int32)
        self.indexes = tf.range(0, tf.shape(self.output)[0]) * tf.shape(self.output)[1] + self.action_holder
        self.responsible_outputs = tf.gather(tf.reshape(self.output, [-1]), self.indexes)

        self.loss = -tf.reduce_mean(tf.log(self.responsible_outputs)*self.reward_holder)

        tvars = tf.trainable_variables()
        self.gradient_holders = []
        for idx,var in enumerate(tvars):
            placeholder = tf.placeholder(tf.float32,name=str(idx)+'_holder')
            self.gradient_holders.append(placeholder)

        self.gradients = tf.gradients(self.loss,tvars)

        optimizer = tf.train.AdamOptimizer(learning_rate=lr)
        self.update_batch = optimizer.apply_gradients(zip(self.gradient_holders,tvars))

    def run(self):
        weights = tf.trainable_variables()[0] #The weights we will evaluate to look into the network.
        total_episodes = 5000 #Set total number of episodes to train agent on.
        max_ep = 300000 # Highest score an episode can reach
        update_frequency = 5

        init = tf.initialize_all_variables()
        with tf.Session() as sess:
            sess.run(init)
            i = 0
            total_reward = []
            total_length = []

            gradBuffer = sess.run(tf.trainable_variables())
            for ix, grad in enumerate(gradBuffer):
                gradBuffer[ix] = grad * 0

            while i < total_episodes:
                # print('GAME RESET')
                self.app.engine.start() # Initialize the game
                running_reward = 0
                ep_history = []
                state = self.app.engine.encode_state()
                for j in range(max_ep):
                    a = self.choose_action(sess, state)
                    self.app.engine.player_direction = a

                    # print()
                    # print('AGENT ACTION: ', a)
                    new_state, reward, done = self.app.step()
                    # print('STEP REWARD: ', reward)
                    # print('DONE: ', done)

                    if a == -1:
                        a = 2

                    ep_history.append([state, a, reward, new_state])
                    state = new_state
                    running_reward += reward
                    time.sleep(0.5)
                    if done == True:
                        ep_history = np.array(ep_history)
                        feed_dict={self.reward_holder:ep_history[:,2],
                                self.action_holder:ep_history[:,1],
                                self.state_in:np.vstack(ep_history[:,0])}
                        grads = sess.run(self.gradients, feed_dict=feed_dict)
                        for idx,grad in enumerate(grads):
                            gradBuffer[idx] += grad

                        if i % update_frequency == 0 and i != 0:
                            feed_dict= dictionary = dict(zip(self.gradient_holders, gradBuffer))
                            _ = sess.run(self.update_batch, feed_dict=feed_dict)
                            for ix,grad in enumerate(gradBuffer):
                                gradBuffer[ix] = grad * 0

                        total_reward.append(running_reward)
                        total_length.append(j)
                        # print(np.mean(total_reward[-100:]))
                        time.sleep(3)
                        break

                # if i % 100 == 0:
                i += 1

    def choose_action(self, sess, state):
        a_dist = sess.run(self.output,feed_dict={self.state_in:[state]})
        a = np.random.choice(a_dist[0],p=a_dist[0])
        a = np.argmax(a_dist == a)
        if a == 2:
            a = -1
        return a
