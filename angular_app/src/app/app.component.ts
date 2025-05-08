import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { CommonModule } from '@angular/common'; // ✅ Import CommonModule
//import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule],
  //imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'pdf-upload';
 
  errorMessage: string = '';  //variable to hold error messages
  successMessage: string = '';
  
  constructor(
    private http:HttpClient
  ){

  }
  name:string = ''
  file:any; 
  fileName:string = ''
  getName(name:string) {
    this.name = name;
  }

  getFile(event:any) {
    this.file = event.target.files[0];
    this.fileName = event.target.files[0].name;
  }

  submitData(){
    console.log('Starting submitData function'); // New log
    this.errorMessage = ''; 
    this.successMessage = ''; 
    const allowedTypes = ['application/pdf', 'application/x-pdf'];
    
    if(!this.file) {
      this.errorMessage = 'No file selected. Please choose a PDF file.';
      return;
    }
  
    const fileExtension = this.file.name.split('.').pop()?.toLowerCase();
    if (!allowedTypes.includes(this.file.type) && fileExtension !== 'pdf')  {
      this.errorMessage = 'Error uploading file. Please upload a valid PDF file.';
      return;
    }
  
    let formData = new FormData();
  formData.append("file",this.file)


    //Submit to API
    this.http.post('http://127.0.0.1:8000/convert', formData, { 
    responseType: 'blob',
    observe: 'response'  // Add this to see full response details
  }).subscribe({
    next: (response: any) => {
      
      if (!response?.body || response.body.size === 0) {
        console.log('Empty response received'); // New log
        this.errorMessage = "Server returned an empty file. Please try again.";
        return;
      }
      this.successMessage = `File "${this.file.name}" was successfully uploaded and processed!`;
      
      
      // This portion allows the file to be automatically
      // downloaded, I am just leaving it commented out
      // so our computers don't get filled with random excel
      // files during testing

      // const fileURL = window.URL.createObjectURL(response);
      // const a = document.createElement('a');
      // a.href = fileURL;
      // a.download = `${this.file.name.replace('.pdf', '')}_data.xlsx`;
      // a.click();
      // window.URL.revokeObjectURL(fileURL);
    },
    error: (error: any) => {
      this.errorMessage = error.error?.detail || 'An unexpected error occurred. Please try again.';
      this.successMessage = ''; 
    }
  });
}}