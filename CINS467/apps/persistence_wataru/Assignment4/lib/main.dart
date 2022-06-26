import 'package:flutter/material.dart';
import 'package:persistence_wataru/db.dart';
import 'package:flutter/widgets.dart';


void main() => runApp(MyApp());

class MyApp extends StatelessWidget {
  // This widget is the root of your application.

  @override

  Widget build(BuildContext context) {
    const appTitle = 'Form Validation Demo';
    return MaterialApp(
      title: 'Hello world',
      // theme: ThemeData(
      //   primarySwatch: Colors.red,
      // ),
      home: Scaffold(
      appBar: AppBar(
        title: const Text(appTitle),
      ),
      body: MyCustomForm(),
      )
    );
  }
}

// Create a Form widget.
class MyCustomForm extends StatefulWidget {
  // const MyCustomForm({super.key});
  const MyCustomForm({Key? key}) : super(key: key);

  @override
  MyCustomFormState createState() {
    return MyCustomFormState();
  }
}

// Create a corresponding State class.
// This class holds data related to the form.
class MyCustomFormState extends State<MyCustomForm> {
  // Create a global key that uniquely identifies the Form widget
  // and allows validation of the form.
  //
  // Note: This is a GlobalKey<FormState>,
  // not a GlobalKey<MyCustomFormState>.
  final _formKey = GlobalKey<FormState>();
  var name ="Wataru";
  var age="29";
  var gender="male";
  var _std;
  void getValues(int i) async{
    final value = await getStudent(i);
    _std = value;
    print(await _std);
  }
  

  
  
  TextEditingController nameController = TextEditingController();
  TextEditingController ageController = TextEditingController();
  TextEditingController genderController = TextEditingController();
  @override
  Widget build(BuildContext context) {
    // Build a Form widget using the _formKey created above.
    db_init();
    getValues(0);
    return Form(
      key: _formKey,
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          TextFormField(
            controller: nameController,
            decoration: InputDecoration(labelText: 'name'),
            // The validator receives the text that the user has entered.
            validator: (String? value) {
              if (value == null || value.isEmpty) {
                return 'Please enter some text';
              }
              return null;
            },
          ),
          TextFormField(
          // The validator receives the text that the user has entered.
            controller: ageController,
            decoration: InputDecoration(labelText: 'age'),
              validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter some text';
              }else if(int.parse(value) <0 &&int.parse(value) >150 ){
                return 'Please put a number between 0 and 150';
              }
              return null;
              },
          ),
          TextFormField(
          // The validator receives the text that the user has entered.
            controller: genderController,
            decoration: InputDecoration(labelText: 'gender'),
              validator: (value) {
              if (value == null || value.isEmpty) {
              return 'Please enter some text';
              }
              return null;
              },
          ),
          Padding(
            padding: const EdgeInsets.symmetric(vertical: 16.0),
            child: ElevatedButton(
              onPressed: () {
                setState(() {
                  // name = "kakeru";
                  // age = "23";
                  // gender = "male";
                  var std;
                  name = nameController.text;
                  age = ageController.text;
                  gender = genderController.text;
                  std = Student(id: 0, name: name, age: int.parse(age), gender: gender);
                  print(name);
                  print(age);
                  print(gender);
                  updateStudent(std);
                  getValues(0);
                });
                // Validate returns true if the form is valid, or false otherwise.
                if (_formKey.currentState!.validate()) {
                  // If the form is valid, display a snackbar. In the real world,
                  // you'd often call a server or save the information in a database.
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Processing Data')),
                  );
                }
              },
              child: const Text('Update'),
            ),
          ),
        Container(
            
            child: Column(
          children: <Widget>[
            Container(
              child: Text("DB data"),
            ),
            Container(
              child: Text(_std.name),
            ),
            Container(
              child: Text(_std.age.toString()),
            ),
            Container(
              child: Text(_std.gender),
            )
          ],
        ),)
        ],
      ),
    );
  }
}

