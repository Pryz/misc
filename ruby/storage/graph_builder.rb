#!/usr/bin/ruby

require "#{File.dirname(__FILE__)}/storage_collector.rb"
require 'rubygems'
require 'neography'

# i.e storage collector
#{:vgs=>[{:vg=>"vg_root", :pvs=>[{:pv=>"/dev/sda2"}]}],
# :hostname=>"kermit.labo.fr",
# :mounts=>
#  [{:vg=>"vg_root",
#    :lv=>"lv_root",
#    :fs=>"/dev/mapper/vg_root-lv_root",
#    :mount=>"/"}]}
Neography.configure do |config|
  config.protocol       = "http://"
  config.server         = "puppet.labo.fr"
  config.port           = 7474
  config.directory      = ""  # prefix this path with '/' 
  config.cypher_path    = "/cypher"
  config.gremlin_path   = "/ext/GremlinPlugin/graphdb/execute_script"
  config.log_file       = "neography.log"
  config.log_enabled    = false
  config.max_threads    = 20
  config.authentication = nil  # 'basic' or 'digest'
  config.username       = nil
  config.password       = nil
  config.parser         = {:parser => MultiJsonParser}
end

@collector = StorageCollector.new
@neo = Neography::Rest.new

# get storage data
storage = @collector.get_local_storage
pp storage
host = @neo.create_node("name" => storage[:hostname])
storage[:mounts].each do |mnt_data|
    lv = @neo.create_node("name" => mnt_data[:mount], "lv" => mnt_data[:lv], "fs" => mnt_data[:fs])
    @neo.create_relationship("lv_in_host", lv, host)

    vg = @neo.create_node("name" => mnt_data[:vg])
    @neo.create_relationship("lv_to_vg", lv, vg)
    storage[:vgs].each do |volg|
        if volg[:vg] == mnt_data[:vg]
            volg[:pvs].each do |pv|
                pv_node = @neo.create_node("name" => pv[:pv])
                @neo.create_relationship("vg_in_pv", vg, pv_node)
            end
        end
    end
end
