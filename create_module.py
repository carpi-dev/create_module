#!/usr/bin/python3

from argparse import ArgumentParser
from os.path import isdir, join
from os import mkdir


TPL_CMAKELISTS = """cmake_minimum_required(VERSION 3.1.0)
project({1})

if(CMAKE_VERSION VERSION_LESS "3.7.0")
    set(CMAKE_INCLUDE_CURRENT_DIR ON)
endif()

set(CMAKE_CXX_STANDARD 11)
add_compile_definitions({2}_LOADABLE)

set(CMAKE_AUTOMOC ON)
set(CMAKE_AUTORCC ON)
set(CMAKE_AUTOUIC ON)

find_package(Qt5 COMPONENTS Widgets REQUIRED)

add_library({1} SHARED
        {0}_global.h
        {0}.cpp
        {0}.h
        )

target_link_libraries({1} PUBLIC Qt5::Widgets)
target_compile_definitions({1} PUBLIC {2}_LIBRARY)

install(TARGETS {1}
        LIBRARY DESTINATION lib/carpi)
"""


TPL_CPP = """#include "{0}.h"

#ifdef {2}_LOADABLE
#include "ui_{1}.h"
#endif

{0}::{0}(QWidget *parent): QWidget(parent), 
#ifdef {2}_LOADABLE
ui(new Ui::{0})
#endif
{
#ifdef {2}_LOADABLE
    ui->setupUi(this);
#endif
    // todo signals and slots for labels
}

{0}::~{0}()
{
#ifdef {2}_LOADABLE
    delete ui;
#endif
}

#ifdef {2}_LOADABLE
extern "C" {2}_EXPORT QWidget* create() {
    return new {0}();
}

extern "C" {2}_EXPORT char* getName() {
    return (char*) "{0}";
}

extern "C" {2}_EXPORT int getDefaultIndex(){
    return -1;
}

extern "C" {2}_EXPORT QStringList getSettingsKeys(){
    return QStringList(); // << KEY_SOMETHING_SOMETHING
}

extern "C" {2}_EXPORT QStringList getDependencies(){
    return QStringList(); // << "something"
}

extern "C" {2}_EXPORT int getVersion(){
    return 1;
}
#endif
"""

TPL_H = """#ifndef CARPI_QT_{2}_H
#define CARPI_QT_{2}_H

#ifdef {2}_LOADABLE
#include "{0}_global.h"
#endif

#include <QWidget>

#ifdef {2}_LOADABLE
QT_BEGIN_NAMESPACE
namespace Ui { class {0}; }
QT_END_NAMESPACE
#endif

class {0} : public QWidget
{
Q_OBJECT
private:
#ifdef {2}_LOADABLE
    Ui::{0} *ui;
#endif

public:
    explicit {0}(QWidget *parent = nullptr);
    ~{0}() override;
};

#ifdef {2}_LOADABLE
extern "C" {
    {2}_EXPORT int getDefaultIndex();
    {2}_EXPORT char* getName();
    {2}_EXPORT QWidget* create();
    {2}_EXPORT int getVersion();
    {2}_EXPORT QStringList getSettingsKeys();
    {2}_EXPORT QStringList getDependencies();
};
#endif

#endif //CARPI_QT_{2}_H
"""

TPL_GLOBAL_H = """#ifndef CARPI_QT_{0}_GLOBAL_H
#define CARPI_QT_{0}_GLOBAL_H

#include <QtCore/qglobal.h>

#if defined({0}_LIBRARY)
#  define {0}_EXPORT Q_DECL_EXPORT
#else
#  define {0}_EXPORT Q_DECL_IMPORT
#endif

#endif //CARPI_QT_{0}_GLOBAL_H
"""

TPL_UI = """<?xml version="1.0" encoding="UTF-8"?>
<ui version="4.0">
 <class>{0}</class>
 <widget class="QWidget" name="{0}">
  <property name="geometry">
   <rect>
    <x>0</x>
    <y>0</y>
    <width>1024</width>
    <height>600</height>
   </rect>
  </property>
  <property name="windowTitle">
   <string>Form</string>
  </property>
  <property name="styleSheet">
   <string notr="true">background-color: rgb(0, 0, 0);</string>
  </property>
 </widget>
 <resources/>
 <connections/>
</ui>
"""


def create(fn, tpl):
    print("creating '{0}'".format(fn))
    with open(fn, "w") as o:
        o.write(tpl)


def main():
    ap = ArgumentParser()
    ap.add_argument("-n", "--name", help="module name", required=True, type=str)
    a = ap.parse_args()

    if isdir(a.name):
        print("module '{0}' already exists".format(a.name))
        exit()

    print("creating directory '{0}'".format(a.name))
    mkdir(a.name)

    create(join(a.name, "CMakeLists.txt"), TPL_CMAKELISTS.format(a.name, a.name.lower(), a.name.upper()))
    create(join(a.name, "{0}.cpp".format(a.name)), TPL_CPP.replace("{0}", a.name)
           .replace("{1}", a.name.lower()).replace("{2}", a.name.upper()))
    create(join(a.name, "{0}.h".format(a.name)), TPL_H.replace("{0}", a.name)
           .replace("{1}", a.name.lower()).replace("{2}", a.name.upper()))
    create(join(a.name, "{0}_global.h".format(a.name)), TPL_GLOBAL_H.format(a.name.upper()))
    create(join(a.name, "{0}.ui".format(a.name.lower())), TPL_UI.format(a.name))


if __name__ == '__main__':
    main()
