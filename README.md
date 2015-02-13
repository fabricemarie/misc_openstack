OpenStack Miscellaneous Tools
===

create_volumes_sequentially.py
---
**Case**: you want to create a large number of volumes
**Problem**: you do not want to create them all simultaneously to not overload unnecessarily the storage backend.
**Solution 1**: you write a quick `for` loop in shell that calls `cinder create`... for each volume and then `sleep` before creating the next one. This kind of quick shell script works fine, but has obvious limitations: it does not check for errors, it does not wait for the previous volume to be created before continuing, it merely sleeps an arbitrary amount of time then goes on.
**Solution 2**: write a proper shell script or other proper python script that loops through the creation of each volume and waits each time for the volume to be created before moving on to the next.

**Synopsis**:
Easily create a series of volumes with the same properties one after the other.

**Usage**:

```
usage: create_volumes_sequentially.py
    [-h] [--os-username username]
    [--os-password password]
    [--os-tenant-name tenant_name]
    [--os-auth-url auth_URL]
    [--name template] --size GB_size
    --volume-type voltype_name
    [--poll-frequency seconds]
    --number-volumes number
    [--start-index index]
    [--image-id ID] [--snapshot-id ID]
    [--source-volid ID]
    [--availability-zone zone]
    [--version]

Create multiple similar cinder volumes one after the other.

optional arguments:
  -h, --help
      show this help message and exit
  --os-username username
      The OpenStack user's username to use to connect to
      OpenStack Keystone
  --os-password password
      The OpenStack user's password to use to connect to
      OpenStack Keystone
  --os-tenant-name tenant_name
      The OpenStack user's tenant name to use to connect to
      OpenStack Keystone
  --os-auth-url auth_URL
      The OpenStack Keystone authentication URL
  --name template
      The volume name template to use, after which we will
      add a dash and an index number. Defaults to 'volume'
  --size GB_size
      The size in GB of each volume to create
  --volume-type voltype_name
      The cinder volume-type name to use for volume creation
  --poll-frequency seconds
      The frequency in seconds at which to poll cinder for
      completion. Defaults to 30.
  --number-volumes number
      The number of cinder volumes to create
  --start-index index
      The index to start with for volume creation, this
      index is incremented at each volume created. Defaults
      to 1.
  --image-id ID
      Create volume from image id. Defaults to None
  --snapshot-id ID
      Create volume from snapshot id. Default None
  --source-volid ID
      Create volume from volume id. Defaults to None.
  --availability-zone zone
      Availability zone for volume. Defaults to None.
  --version
      show program's version number and exit

Copyright (c) 2015 Kibin Labs Pte Ltd. Released under MIT license.
```

**Example**:
```
# ./create_volumes_sequentially.py --size 1 --volume-type cinder_iSCSI --number-volumes 3 --start-index 3 
2015-02-13 09:49:31,079 [INFO] Initiated creation of volume volume-3 with volume-id 84d4ce85-3461-480d-b8bf-b910af41257b
2015-02-13 09:49:32,159 [INFO] Waiting for volume volume-3. Current state is 'creating'. Sleeping 30 seconds.
2015-02-13 09:50:03,872 [INFO] Successfully created volume volume-3
2015-02-13 09:50:06,480 [INFO] Initiated creation of volume volume-4 with volume-id 223a1f0d-2c88-4436-b517-2555b002db44
2015-02-13 09:50:07,825 [INFO] Waiting for volume volume-4. Current state is 'creating'. Sleeping 30 seconds.
2015-02-13 09:50:39,071 [INFO] Successfully created volume volume-4
2015-02-13 09:50:40,371 [INFO] Initiated creation of volume volume-5 with volume-id 139c8663-c01e-4994-a46e-16311f3c3f72
2015-02-13 09:50:41,598 [INFO] Waiting for volume volume-5. Current state is 'creating'. Sleeping 30 seconds.
2015-02-13 09:51:12,822 [INFO] Successfully created volume volume-5
```
