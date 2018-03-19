import numpy as np
import sys
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data
from util import seq


mnist = input_data.read_data_sets("MNIST_data/", one_hot=True)

# set training data (x, y)
x = tf.placeholder(tf.float32, [None, 784])
y_ = tf.placeholder(tf.float32, [None, 10])

model = seq(x , y_ , 784)
for _ in range(2):
	model.add_FC(10)
	model.add_activate(tf.nn.relu)

model.add_FC(10)
sess = tf.Session()
pred_y_ , train_step = model.get_train(sess)
tf.global_variables_initializer().run(session=sess)
print("\n{0:-^40s}\n".format("all param:" + str(model.summary())))
Acc = np.empty(shape=[0, 1])
grad_norm = np.empty(shape=[0, 1])
# var_grad = tf.gradients(loss, x)[0]
for _ in range(2000):
	trainX , trainY = mnist.train.next_batch(1000)
	sess.run(train_step,feed_dict={
			x : trainX,
			y_ : trainY
		})
	grad = sess.run(tf.gradients(model.loss, ???)[0], feed_dict={
		x : trainX,
		y_ : trainY
	})

	norm = np.sqrt(np.sum(np.square(grad)))
	accuracy = model.get_acc(mnist.train.images, mnist.train.labels)
	Acc = np.append(Acc, np.array([accuracy])).reshape(-1, 1)
	grad_norm = np.append(grad_norm, np.array([norm])).reshape(-1, 1)
	if _ % 100 == 0:
		print ("epoch %d acc %8g " %(_,accuracy))

np.savetxt("csvdir/1-2_acc.csv", Acc)
np.savetxt("csvdir/1-2_grad_norm.csv", grad_norm)