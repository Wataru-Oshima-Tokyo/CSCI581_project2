import 'dart:async';

import 'package:flutter/widgets.dart';
import 'package:path/path.dart';
import 'package:sqflite/sqflite.dart';

Future<Database> getDatabase() async{
  final database = openDatabase(
    // Set the path to the database. Note: Using the `join` function from the
    // `path` package is best practice to ensure the path is correctly
    // constructed for each platform.
    join(await getDatabasesPath(), 'student_database.db'),
    // When the database is first created, create a table to store students.
    onCreate: (db, version) {
      // Run the CREATE TABLE statement on the database.
      return db.execute(
        'CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, name TEXT, age INTEGER, gender TEXT)',
      );
    },

    // Set the version. This executes the onCreate function and provides a
    // path to perform database upgrades and downgrades.
    version: 1,
  );
  return database;
}

void db_init() async {
  // Avoid errors caused by flutter upgrade.
  // Importing 'package:flutter/widgets.dart' is required.
  WidgetsFlutterBinding.ensureInitialized();
  // Open the database and store the reference.
  final db = await getDatabase();
  List<Map<String, dynamic>> maps = await db.query(
    'students',
    // Use a `where` clause to delete a specific student.
    where: 'id = ?',
    // Pass the Student's id as a whereArg to prevent SQL injection.
    whereArgs: [0],

  );

  if(maps.isEmpty){
    var std = const Student(id: 0, name: "Wataru", age: 29, gender: "Male");
    await insertStudent(std);
    print(await students());
  }
  //
  //
  //
  //
  // var fido = const Student(
  //   id: 0,
  //   name: 'Fido',
  //   age: 35,
  //   gender: "Male"
  // );
  //
  // await insertStudent(fido);
  //
  // // Now, use the method above to retrieve all the students.
  // print(await students()); // Prints a list that include Fido.
  //
  // // Update Fido's age and save it to the database.
  // fido = Student(
  //   id: fido.id,
  //   name: fido.name,
  //   age: fido.age + 7,
  //   gender: fido.gender,
  // );
  // await updateStudent(fido);
  //
  // // Print the updated results.
  // print(await students()); // Prints Fido with age 42.
  //
  // // Delete Fido from the database.
  // await deleteStudent(fido.id);
  //
  // // Print the list of students (empty).
  // print(await students());
}

// Create a Student and add it to the students table
Future<void> insertStudent(Student student) async {
  // Get a reference to the database.
  final db = await getDatabase();

  // Insert the Student into the correct table. You might also specify the
  // `conflictAlgorithm` to use in case the same student is inserted twice.
  //
  // In this case, replace any previous data.
  await db.insert(
    'students',
    student.toMap(),
    conflictAlgorithm: ConflictAlgorithm.replace,
  );
}


Future<void> deleteStudent(int id) async {
  // Get a reference to the database.
  final db = await getDatabase();

  // Remove the Student from the database.
  await db.delete(
    'students',
    // Use a `where` clause to delete a specific student.
    where: 'id = ?',
    // Pass the Student's id as a whereArg to prevent SQL injection.
    whereArgs: [id],
  );
}



Future<void> updateStudent(Student student) async {
  // Get a reference to the database.
  final db = await getDatabase();

  // Update the given Student.
  await db.update(
    'students',
    student.toMap(),
    // Ensure that the Student has a matching id.
    where: 'id = ?',
    // Pass the Student's id as a whereArg to prevent SQL injection.
    whereArgs: [student.id],
  );
}


Future<List<Student>> students() async {
  // Get a reference to the database.
  final db = await getDatabase();

  // Query the table for all The Student.
  final List<Map<String, dynamic>> maps = await db.query('students');

  // Convert the List<Map<String, dynamic> into a List<Student>.
  return List.generate(maps.length, (i) {
    return Student(
      id: maps[i]['id'],
      name: maps[i]['name'],
      age: maps[i]['age'],
      gender: maps[i]['gender'],
    );
  });
}

Future<Student> getStudent(int i) async {
  final db = await getDatabase();
  final List<Map<String, dynamic>> maps = await db.query('students');
  return Student(
    id: maps[i]['id'],
    name: maps[i]['name'],
    age: maps[i]['age'],
    gender: maps[i]['gender'],
  );
}



class Student {
  final int id;
  final String name;
  final int age;
  final String gender;

  const Student({
    required this.id,
    required this.name,
    required this.age,
    required this.gender,
  });

  // Convert a Student into a Map. The keys must correspond to the names of the
  // columns in the database.
  Map<String, dynamic> toMap() {
    return {
      'id': id,
      'name': name,
      'age': age,
      'gender': gender,
    };
  }

  // Implement toString to make it easier to see information about
  // each student when using the print statement.
  @override
  String toString() {
    return 'Stundet{id: $id, name: $name, age: $age, gender: $gender}';
  }
}