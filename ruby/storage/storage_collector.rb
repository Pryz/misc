#!/usr/bin/ruby

require 'pp'
require 'socket'
require 'rubygems'
require 'lvm'
require 'sys/filesystem'
include Sys

class StorageCollector
    # Get the filesystem corresponding to a LV
    def get_mount(lv_name)
        Filesystem.mounts do |mnt|
            return mnt if mnt.name.match(/#{lv_name}/)
        end
        nil
    end

    # Get storage informations : filesystem, lv, vg and pv
    def get_local_storage
        storage = {:hostname => Socket.gethostname, :mounts => [], :vgs => []}

        LVM::LVM.new({:command => "/usr/bin/sudo /sbin/lvm"}) do |lvm|
            lvm.volume_groups.each do |vg|
                vg.logical_volumes.each do |lv|
                    mnt = get_mount(lv.name)
                    fs = {:mount => mnt.mount_point, :fs => mnt.name, :lv => lv.name, :vg => vg.name}
                    storage[:mounts] << fs
                end

                volg = {:vg => vg.name, :pvs => []}
                vg.physical_volumes.each do |pv|
                    volg[:pvs] << {:pv => pv.name}
                end
                storage[:vgs] << volg
            end
        end
        storage
    end
end

#collector = StorageCollector.new
#pp collector.get_local_storage
