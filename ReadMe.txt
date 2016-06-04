View Frustum Culling
======================

Given a texture model (.obj) file and a pose the program renders a view.
This package has ROS-service interface. 

Contact
-----------
Kejie Qiu <kqiuaa@ust.hk>
Manohar Kuse <mpkuse@connect.ust.hk> 


How to run
-------------
-1-
Run roscore

-2-
Run the rgb_d.py. Be sure to correctly specify the object file (.obj) in this core.
	$ rosrun reference3d_srv rgb_d.py
NOTE: Wait until the rgb_d.py gives a `service ready` message before calling the service.

-3-
Make a service request for the service `/render_two_reference_images`. We provide a sample python script for it.
You can also do this request with ros-c++ interface. Check the tutorial on ros-service. 

	$ rosrun reference3d_srv client.py


