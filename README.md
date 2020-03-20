# Django Web-App: Ride Sharing Service (HW1 for ECE 568 ERSS 2020 Spring)

By Wenge Xie, Chixiang Zhang

## Set Up

To run the program, go to ```docker-deploy/``` folder, then run

```
sudo docker-compose up
```

To visit the website (the login page), type ```your_host_name:8000``` on a web browser.

## Sign Up

When signing up succeeds, the page will be instantly redirected to the login page. If an invalid sign up occurs, the page will not be redirected.

## Ride Lists

A user is able to access all her/his related and uncompleted rides by clicking boxes named ```Check...```, and our App will direct the user to a list of related rides.

User's completed rides can be retrieved by clicking boxes named  ```Check...history```.

## Create a Ride

In order to create a ride as a drive owner, the pickup time should be at least 5 minutes later than current time.

The input format of time must be exactly the same as the example below:

```
2020-02-06 22:16:20
```

This example equals ```10:16pm, 20sec, Feb.6, 2020```, and the same format was applied to all time-related forms you will write to. 

The number of passengers was restricted to 1-20, which stands for the ride owner's party (include her/himself).

The ride owner can determine whether to assign a vehicle type to her/his ride or not.

The ride owner can also determine whether to specify a special request or not on the text box.

When a ride is created, its status is automatically set to ```Open```.

## Join a Ride

When click ```Join a ride``` on home page, the App will direct the user to a searching page for she/he to search sharable rides.

In the searching page, similar to what was restricted in ```Create a Ride```, the earliest pickup time should be at least 5 minute later than current time. The latest pickup time should be later than the earliest pickup time. And the owner's pickup time should be in the arrival window.

The number of passengers was restricted to 1-20, which stands for the ride sharer's party (include her/himself).

By clicking ```Search for sharable rides```, the user will be directed to a ```Into ride``` page containing the list of all sharable rides.

## Take a Ride

Ride sharer can take any ride in the ```Into ride``` page by simply clicking on the ```Take!``` button.

## Edit a Ride

Both ride owner and ride sharer are able to edit his related ride by clicking ```Edit``` button on whatever a page that displays a list of available rides, if these rides are not be confirmed (or taken) by a driver.

As for a ride owner, she/he should be able to edit destination (dest), pickup time, vehicle type and special requests in the ride edit page. We currently not write any response on ride sharer's side if any attributes of a ride is modified by its ride owner, but all ride sharers should receive an Email that notifies the ride information was modified. 

A ride owner could modify the sharable status only if this ride is currently not sharable.

As for a ride sharer, she/he is only allowed to modify the passenger number of the party of her/himself.

## View Ride Details

When a ride is not competed, its information can be viewed by any ride owner, sharer and driver that has a relation to this ride by direct clicking the ```View``` button in any webpage that displays a list of rides.

## Cancel a Ride

A ride can be canceled before it is confirmed by a driver by both ride owner and ride sharer. For a ride owner, a ride cancellation indicates that this ride is also canceled for all ride sharers. As for a ride sharer. For a ride sharer, a ride cancellation indicates that only this sharer quit this ride, and all other sharers and the owner are still remained on this ride.

## Promote to Driver

A user can promote by driver by clicking ```Become a driver``` button on the home page.

Vehicle special info is a optional field to input.

## Take a Ride

In the home page, ```Take a ride``` button makes a driver user to search an available ride to take as a driver. 

If a ride has vehicle type specified by the ride owner, only drivers with the same vehicle time can see this ride on the ride list. 

If a ride has special requests specified by the ride owner, only drivers with the same content in her/his special vehicle info can see this ride onf the ride list.

A driver cannot see any ride whose passenger number exceeds her/his vehicle capacity.

The driver can take a ride by clicking ```Take!``` button under any ride shown on the ride list.

When a ride was taken by a driver, the status of a ride will be switched to ```Confirmed``` and an Email will be sent to the ride owner and all ride sharers sharing this ride.

## Complete a Ride

In the ```taken rides``` page, a driver can cancel any not-completed rides she/he has taken by clicking ```Complete``` button below each ride. When a ride is complete, its status will be ended up to ```Completed``` and an Email will be sent to the ride owner and all ride sharers sharing this ride.

## Edit User Profile

Password are not allowed by be modified right now.

As for a driver, she/he can modify the vehicle information only when no ride is taken at that time.