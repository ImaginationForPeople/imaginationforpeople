#!/usr/bin/env ruby

require 'find'
require 'pp'


class RefChecker
	# An HTML file, referenced from somewhere
	class IncludeHtmlRef
		attr_reader :refname, #the file referenced
			:from_file, #from where
			:from_line,
			:as # :include (from html), :extend (from html) or :render (from view)

		def initialize 
		end
	end

	# An view method, referenced from html
	class ViewHtmlRef
	end

	# A method from a view, somewhere

	def initialize root_path
		@root_path = root_path
	end

	def each_apps where
		Find.find(where) do |path|
			next if path == where
			if File.directory? path then
				yield File.basename(path), 
					path
				Find.prune
			end
		end
	end

	def each_html where
		Find.find(where) do |path|
			next if path == where

			if path =~ /.html$/ then
				yield path.gsub(where + '/','')
			end
		end
	end

	def run
		views_list = []
		html_list = {}

		apps_path = File.join @root_path, 'apps'
		each_apps(apps_path) do |app_name, app_path|
			view_path = File.join(app_path,'views.py')
			#parse_view , app_name
			puts "VIEW = %s" % view_path 

			app_templates_path = File.join app_path, 'templates'
			each_html(app_templates_path) do |html_path|
				if html_list.has_key? html_path then
					html_list[html_path] << app_name
				else
					html_list[html_path] = [app_name]
				end
				#puts "(%s) = %s" % [app_name, html_path]
			end
		end


		# check for html name collisions between apps
		html_list.each do |html_path, apps|
			if apps.length > 1 then 
				raise "ERROR: #{html_path} is referenced by multiple apps: #{apps.inspect}" 
			end
		end

		# create references from views
		# check that there is no dangling render link
		# (and mark html files as referenced)

		# create references from html
		# check that there is no dangling include link
		# (and mark html files as referenced)
		
		# check for unreferenced files
		#
	end
end

root_path = File.join(File.dirname(__FILE__),'..')
refcheck = RefChecker.new root_path
refcheck.run

