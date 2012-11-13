#!/usr/bin/ruby

require 'rubygems'
require 'curb'
require 'json'
require 'pp'

get_repos = Curl.get("https://api.github.com/users/thinkfr/repos")

arr_repos = []

repos = JSON.parse(get_repos.body_str)
repos.each do |repo|
  get_issues = Curl.get("https://api.github.com/repos/#{repo['full_name']}/issues")
  arr_issues = []

  issues = JSON.parse(get_issues.body_str)

  issues.each do |issue|
    label = "none"
    if issue.has_key?("labels") and issue["labels"][0]
        label = issue["labels"][0]["name"]
    end
    info_issue = {:title => issue["title"], :label => label}
    arr_issues << info_issue
  end
  arr_issues.sort_by { |issue| issue[:label] }
  arr_repos << {:name => repo['full_name'], :issues => arr_issues}
end

pp arr_repos.inspect
