#!/usr/bin/env ruby

require 'find'
require 'pp'


class RefChecker

	class MissingFileError < RuntimeError
		def initialize file, ref
			super()
			@file = file
			@ref = ref
		end

		def to_s
			[ 
				"#  Missing reference :",
				"%s" % @file.to_s,
				"",
				"# Was referenced by :",
				"%s" % @ref.to_s
			].join("\n")
		end
	end

			
	class HtmlFile
		attr_reader :used, :app, :path, :refs

		def initialize app, path
			@app = app
			@path = path
			@refs = []
		end

		def add_ref ref_obj
			@refs << ref_obj
		end

		def used?
			(not @refs.empty?)
		end

		def to_s 
			"File '%s' from app '%s'\n" % [@path, @app]
		end
	end

	class GenericRef
		attr_reader :path, #the file referenced
			:from_file, #from where
			:from_line,
			:from_ctx,
			:as # :include (from html), :extend (from html) or :render (from view)

		def initialize attributes={}
			@path = nil
			@from_file = nil
			@from_line = nil
			@from_ctx = nil

			# dirty init
			attributes.each do |k,v|
				if instance_variables.include? :"@#{k}" then
					instance_variable_set("@#{k}", v) unless v.nil?
				end
			end
		end

		def to_s
			"%s at line" % [@from_file, @from_line]
		end
	end

	# An HTML file, referenced from somewhere
	class IncludeHtmlRef < GenericRef ; end

	# An view method, referenced from html
	class ViewHtmlRef < GenericRef ; end

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

			if path =~ /\.html$/ then
				yield path.gsub(where + '/','')
			end
		end
	end

	def build_html_hash html_list
		html_hash = {}

		# we build the hash
		html_list.each do |htmlfile|
			if html_hash.has_key? htmlfile.path then
				html_hash[htmlfile.path] << htmlfile
			else
				html_hash[htmlfile.path] = [htmlfile]
			end
		end
		return html_hash
	end

	def build_html_path app, path
		File.join @root_path, "apps", app, "templates", path
	end

	def build_view_path app
		File.join @root_path, app, 'views.py'
	end

	def validate_html_noncollision html_hash
		html_hash.each do |html_path, htmlfiles|
			if htmlfiles.length > 1 then 
				raise "ERROR: #{html_path} is referenced by multiple apps: #{htmlfiles.inspect}" 
			end
		end
	end

	def validate_nonbroken_view view_list, html_hash
		ref_list = []
		view_list.each do |view_path|
			File.open(view_path) do |fh|
				count = 0
				fh.readlines.each do |line|
					count += 1
					line.strip!
					case line
					when /\"(.*\.html)\"/ then
						ref_list << (
							ViewHtmlRef.new :path => $1, 
							:from_ctx => line, 
							:from_line => count,
							:from_file => view_path
						)

					when /(['"])(.*\.html)\1/ then
						ref_list << (
							ViewHtmlRef.new :path => $2, 
							:from_ctx => line, 
							:from_line => count,
							:from_file => view_path
						)
					end
				end
			end
		end

		# resolve, add reference & check
		ref_list.each do |ref|
			if html_hash.has_key? ref.path then
				html_hash[ref.path].first.add_ref ref
			else
				raise MissingFileError.new(ref.path, ref)
			end
		end
	end


	def validate_nonbroken_include html_list, html_hash
		ref_list = []
		html_list.each do |htmlfile|
			html_path = build_html_path htmlfile.app, htmlfile.path
			File.open(html_path) do |fh|
				count = 0
				fh.readlines.each do |line|
					line.strip!

					case line
					when /include.*? \"(.*\.html)\"/ then
						ref_list << (
							ViewHtmlRef.new :path => $1, 
							:from_ctx => line, 
							:from_line => count,
							:from_file => htmlfile
						)
					when /include.*? (['"])(.*\.html)\1/ then
						ref_list << (
							ViewHtmlRef.new :path => $2, 
							:from_ctx => line, 
							:from_line => count,
							:from_file => htmlfile
						)
					end
				end #readlines
			end 
		end

		# resolve, add reference & check
		ref_list.each do |ref|
			relfile = File.join( File.dirname(ref.from_file.path), ref.path )
			relapp = ref.from_file.app
			rel_path = build_html_path relapp, relfile

			if html_hash.has_key? ref.path then
				html_hash[ref.path].first.add_ref ref
			elsif html_hash.has_key? relfile then
				# FIXME: validate that it is the same app !
				html_hash[relfile].first.add_ref ref
			else
				pp "APP", relapp,
					"PATH", relfile
				raise MissingFileError.new(ref.path, ref)
			end
		end
	end


	def validate_nonreferenced html_list
		html_list.select do |htmlfile|
			htmlfile.refs.length < 1
		end.each do |htmlfile|
			STDOUT.puts "  Missing reference for %s : %s" % [htmlfile.app, htmlfile.path]
		end
	end

	def run
		view_list = []
		html_list = []

		apps_path = File.join @root_path, 'apps'
		each_apps(apps_path) do |app_name, app_path|
			view_path = build_view_path app_name
			if File.exist? view_path then
				view_list << view_path
			end

			app_templates_path = File.join app_path, 'templates'
			each_html(app_templates_path) do |html_path|
				html_list << HtmlFile.new(app_name, html_path)
			end
		end

		# Prerequisite
		html_hash = build_html_hash html_list

		# check for html name collisions between apps
		# Build hash

		begin
		STDOUT.puts "+ Checking for collisions in HTML relative names... "
		validate_html_noncollision html_hash

		# create references from views
		# check that there is no dangling render link
		# (and mark html files as referenced)
		STDOUT.puts "+ Checking for broken renders from view.py... "
		validate_nonbroken_view view_list, html_hash

		# create references from html
		# check that there is no dangling include link
		# (and mark html files as referenced)
		STDOUT.puts "+ Checking for broken includes from HTML files... "
		validate_nonbroken_include html_list, html_hash
		
		# check for unreferenced files
		STDOUT.puts "+ Checking for unreferenced HTML files... "
		validate_nonreferenced html_list
		rescue MissingFileError => e
			STDERR.puts e
		end
	end
end

p = RefChecker::IncludeHtmlRef.new :path => 'somewhere'

root_path = File.join(File.dirname(__FILE__),'..')
refcheck = RefChecker.new root_path
refcheck.run


