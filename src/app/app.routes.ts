import { Routes } from '@angular/router';
import { SummaryScreenComponent } from './component/summary-screen.component/summary-screen.component';
import { ReviewInvoiceComponent } from './component/review-invoice.component/review-invoice.component';
import { UploadInvoiceComponent } from './component/upload-invoice.component/upload-invoice.component';

export const routes: Routes = [
    {path:'summary', component: SummaryScreenComponent},
    {path: 'review', component: ReviewInvoiceComponent},
    {path:'upload-invoice', component:UploadInvoiceComponent}
];
